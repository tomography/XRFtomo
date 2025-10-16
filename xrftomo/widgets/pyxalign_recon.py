import os
import cupy as cp
import numpy as np
from PyQt5.QtWidgets import QApplication
try:
    from pyxalign import options as opts
    from pyxalign.api import enums
    from pyxalign.api.types import r_type
    from pyxalign.data_structures.xrf_task import XRFTask
    from pyxalign.io.loaders.xrf.api import (
        convert_xrf_projection_dicts_to_arrays,
        load_data_from_xrf_format,
    )
    from pyxalign.io.loaders.xrf.options import XRFLoadOptions
    from pyxalign.test_utils_2 import CITestArgumentParser, CITestHelper
    from pyxalign.plotting.interactive.xrf import XRFProjectionsViewer, XRFVolumeViewer
    PYXALIGN_AVAILABLE = True
except ImportError:
    PYXALIGN_AVAILABLE = False
    opts = None
    enums = None
    r_type = None
    XRFTask = None
    convert_xrf_projection_dicts_to_arrays = None
    load_data_from_xrf_format = None
    XRFLoadOptions = None
    CITestArgumentParser = None
    CITestHelper = None
    XRFProjectionsViewer = None
    XRFVolumeViewer = None


def run_full_test_xrf_data_type_1(
    update_tester_results: bool = False,
    save_temp_files: bool = False,
    test_start_point = None,  # not yet used
):
    if not PYXALIGN_AVAILABLE:
        raise ImportError("pyxalign package is required for this function but is not installed")
    # Setup the test
    ci_options = opts.CITestOptions(
        test_data_name=os.path.join("2ide", "2025-1_Lamni-4"),
        update_tester_results=update_tester_results,
        proj_idx=list(range(0, 750, 150)),
        save_temp_files=save_temp_files,
    )
    ci_test_helper = CITestHelper(options=ci_options)
    # define a downscaling value for when volumes are saved to prevent
    # saving files large files
    s = 4

    # Setup default gpu options
    n_gpus = cp.cuda.runtime.getDeviceCount()
    gpu_list = list(range(0, n_gpus))
    multi_gpu_device_options = opts.DeviceOptions(
        gpu=opts.GPUOptions(
            n_gpus=n_gpus,
            gpu_indices=gpu_list,
            chunk_length=20,
        )
    )

    # if not projection_matching_only:
    checkpoint_list = [enums.TestStartPoints.BEGINNING]
    if test_start_point in checkpoint_list:
        ### Load ptycho input data ###

        folder = ci_test_helper.inputs_folder
        xrf_load_options = XRFLoadOptions()
        xrf_standard_data_dict, extra_PVs = load_data_from_xrf_format(folder, xrf_load_options)
        scan_0 = list(extra_PVs.keys())[0]
        lamino_angle = float(extra_PVs[scan_0]["2xfm:m12.VAL"])

        # Load data
        xrf_array_dict = convert_xrf_projection_dicts_to_arrays(
            xrf_standard_data_dict,
            pad_with_mode=True,
        )

        for channel, projection_array in xrf_array_dict.items():
            ci_test_helper.save_or_compare_results(
                projection_array[:3], f"input_projections_{channel}"
            )

        # Insert data into an XRFTask object
        primary_channel = "Ti"
        xrf_task = XRFTask(
            xrf_array_dict=xrf_array_dict,
            angles=xrf_standard_data_dict[primary_channel].angles,
            scan_numbers=xrf_standard_data_dict[primary_channel].scan_numbers,
            alignment_options=opts.AlignmentTaskOptions(),
            projection_options=opts.ProjectionOptions(
                experiment=opts.ExperimentOptions(laminography_angle=90 - lamino_angle),
            ),
            primary_channel=primary_channel,
        )

        # remove bad data
        xrf_task.drop_projections_from_all_channels(remove_scans=[xrf_task.scan_numbers[143]])

        # Update sample thickness and center of rotation
        xrf_task.projection_options.experiment.sample_thickness = 70
        xrf_task.center_of_rotation = np.array([30, 130], dtype=r_type)

        # check projection arrays, angles, cor, and sample thickness for all channels
        for channel, proj in xrf_task.projections_dict.items():
            ci_test_helper.save_or_compare_results(
                proj.data[::s, ::s, ::s], f"pre_pma_projections_{channel}"
            )
            ci_test_helper.save_or_compare_results(proj.angles, f"angles_{channel}")
            ci_test_helper.save_or_compare_results(proj.scan_numbers, f"scan_numbers_{channel}")
            ci_test_helper.save_or_compare_results(
                proj.center_of_rotation, f"center_of_rotation_{channel}"
            )

        # create preliminary reconstructions
        for channel, proj in xrf_task.projections_dict.items():
            proj.get_3D_reconstruction(True)
            # Check/save the preliminary volume
            ci_test_helper.save_or_compare_results(
                proj.volume.data[::s, ::s, ::s], f"pre_pma_volume_{channel}"
            )

        # create dummy mask
        xrf_task.projections_dict[xrf_task._primary_channel].masks = np.ones_like(
            xrf_task.projections_dict[xrf_task._primary_channel].data
        )
        xrf_task.projections_dict[xrf_task._primary_channel].pin_arrays()

        pma_options = xrf_task.alignment_options.projection_matching
        pma_options.keep_on_gpu = True
        pma_options.high_pass_filter = 0.001
        pma_options.min_step_size = 0.005
        pma_options.iterations = 1000
        pma_options.downsample.enabled = True
        pma_options.mask_shift_type = "fft"
        pma_options.projection_shift_type = "fft"
        pma_options.momentum.enabled = True
        pma_options.interactive_viewer.update.enabled = True
        pma_options.interactive_viewer.update.stride = 50

        # Run projection-matching alignment at successively higher resolutions
        scales = [2, 1]
        shift = None
        for i, scale in enumerate(scales):
            pma_options.downsample.scale = scale
            shift = xrf_task.get_projection_matching_shift(initial_shift=shift)
            # Check/save the resulting alignment shifts at each resolution
            ci_test_helper.save_or_compare_results(shift, f"pma_shift_{scale}x")

        # shift all projections
        xrf_task.apply_staged_shift_to_all_channels()

        # create final reconstructions
        for channel, projections in xrf_task.projections_dict.items():
            projections.get_3D_reconstruction(True)
            # Check/save the aligned volume
            ci_test_helper.save_or_compare_results(
                projections.volume.data[::s, ::s, ::s], f"pma_aligned_volume_{channel}"
            )

        # Rotate all of the reconstructions
        for channel, projections in xrf_task.projections_dict.items():
            projections.volume.optimal_rotation_angles = np.array(
                [2.7, 4, 40]
            )  # estimated this manually
            projections.volume.rotate_reconstruction()
            # Check/save the aligned, rotated volume
            ci_test_helper.save_or_compare_results(
                proj.volume.data, f"pma_aligned_rotated_volume_{channel}"
            )
            # Save tiff file
            ci_test_helper.save_tiff(
                projections.volume.data,
                f"pma_aligned_rotated_volume_{channel}.tiff",
            )

        xrf_task.clear_pma_gui_list()

        # print results of the test
        ci_test_helper.finish_test()

        # Launch the volume viewer
        app = QApplication.instance() or QApplication([])
        gui = XRFVolumeViewer(xrf_task)
        gui.show()
        app.exec()

        # Launch the projections viewer
        app = QApplication.instance() or QApplication([])
        gui = XRFProjectionsViewer(xrf_task)
        gui.show()
        app.exec()


def run_it(data, thetas, lami_angle):
    ci_parser = CITestArgumentParser()
    args = ci_parser.parser.parse_args()
    run_full_test_xrf_data_type_1(
        update_tester_results=args.update_results,
        save_temp_files=args.save_temp_results,
        test_start_point=args.start_point,
    )
