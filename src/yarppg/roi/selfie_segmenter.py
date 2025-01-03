"""Detect the face skin region with MediaPipe's selfie segmentation.

This method is very slow (150-200ms per frame) and will not properly work in
a real-time setting. `FaceMeshDetector` should be used instead.

More information on the selfie segmenter can be found here:
<https://ai.google.dev/edge/mediapipe/solutions/vision/image_segmenter#multiclass-model>
"""

import time

import mediapipe as mp
import numpy as np

from ..containers import RegionOfInterest
from ..helpers import get_cached_resource_path
from .detector import RoiDetector

MEDIAPIPE_MODELS_BASE = "https://storage.googleapis.com/mediapipe-models/"
SELFIE_TASK = "image_segmenter/selfie_multiclass_256x256/float32/latest/selfie_multiclass_256x256.tflite"  # noqa: E501


def get_selfie_segmenter_modelfile():
    """Get the filename of the SelfieSegmenter - download file if necessary."""
    task_filename = "selfie_multiclass.tflite"
    return get_cached_resource_path(task_filename, MEDIAPIPE_MODELS_BASE + SELFIE_TASK)


class SelfieDetector(RoiDetector):
    """Face detector based on MediaPipe's selfie segmentation task."""

    def __init__(self, confidence=0.5, **kwargs):
        super().__init__(**kwargs)
        self.confidence = confidence

        modelpath = get_selfie_segmenter_modelfile()
        if modelpath is None:
            raise FileNotFoundError("Could not find or download segmenter model file.")

        base_options = mp.tasks.BaseOptions(model_asset_path=modelpath)
        segmenter_options = mp.tasks.vision.ImageSegmenterOptions(
            base_options=base_options, running_mode=mp.tasks.vision.RunningMode.VIDEO
        )
        self.segmenter = mp.tasks.vision.ImageSegmenter.create_from_options(
            segmenter_options
        )

    def __del__(self):
        self.segmenter.close()

    def detect(self, frame: np.ndarray) -> RegionOfInterest:
        """Identify face skin region and background in the given image."""
        rawimg = frame.copy()
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

        results = self.segmenter.segment_for_video(
            mp_image, int(time.perf_counter() * 1000)
        )

        face_mask = results.confidence_masks[3].numpy_view() > self.confidence
        bg_mask = results.confidence_masks[0].numpy_view() > self.confidence
        return RegionOfInterest(
            face_mask.astype(np.uint8), baseimg=rawimg, bg_mask=bg_mask.astype(np.uint8)
        )
