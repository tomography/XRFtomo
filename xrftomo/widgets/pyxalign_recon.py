
import os
import numpy as np
try:
    import pyxalign
    PYXALIGN_AVAILABLE = True
except ImportError:
    PYXALIGN_AVAILABLE = False

def run_it(lamino_angle, results_folder, center_of_rotation, xrf_array_dict, scan_numbers, thetas, primary_channel, file_paths):

    if not PYXALIGN_AVAILABLE:
        raise ImportError("pyxalign package is required for this function but is not installed")

    # specify projection options
    projection_options = pyxalign.options.ProjectionOptions()
    projection_options.experiment.laminography_angle = lamino_angle
    projection_options.experiment.pixel_size = 1  # unknown for this dataset
    projection_options.experiment.sample_thickness = 70  # an initial guess, can be updated later
    #Question: does it help to know the pixel size?

    #Create the results folder

    # Create the XRFTask object
    xrf_task = pyxalign.data_structures.XRFTask(
        xrf_array_dict=xrf_array_dict,
        angles=thetas,
        scan_numbers=scan_numbers,
        projection_options=projection_options,
        primary_channel=primary_channel,
        file_paths=file_paths,
    )

    xrf_task.center_of_rotation = center_of_rotation  # [30, 130] y=30, x=130

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
    pma_options.prevent_wrapping_from_shift = True
    #Question: what is step size in units of?

    # create a masked region for projection matching alignment; this will be done
    # automatically or with a GUI in the future
    xrf_task.projections_dict[xrf_task._primary_channel].masks = np.ones_like(
        xrf_task.projections_dict[xrf_task._primary_channel].data
    )

    #Start the alignment for 2x downsampling of the projections
    pma_options.downsample.scale = 2
    shift = xrf_task.get_projection_matching_shift()

    # run projection matching alignment at full resolution
    pma_options.downsample.scale = 1
    shift = xrf_task.get_projection_matching_shift(shift)

    # shift all projections
    xrf_task.apply_staged_shift_to_all_channels()

    #Save the aligned task
    aligned_task_path = os.path.join(results_folder, "aligned_xrf_task.h5")
    xrf_task.save_task(aligned_task_path)

    # Get 3D reconstruction
    xrf_task.get_3D_reconstructions_for_all_channels()

    #Launch the volume viewer
    gui = pyxalign.gui.launch_xrf_volume_viewer(xrf_task)

    #Save the aligned volumes as tiffs
    xrf_task.save_volumes_as_tiffs(results_folder=results_folder, file_prefix="aligned_volume_")

