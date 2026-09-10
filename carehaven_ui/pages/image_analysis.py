"""Local, transparent vision-analysis page; it does not fabricate model results."""
from __future__ import annotations
import streamlit as st
from ai.vision.quality import assess_image_quality
from ai.vision.similarity import compare_images
from ai.vision.yolo import YoloDetector, visualize_detections
from carehaven_ui.components.navbar import render_navbar
def render() -> None:
    render_navbar("Image Analysis")
    image = st.file_uploader("Upload image", type=["jpg", "jpeg", "png", "webp"])
    if not image: return
    data = image.getvalue(); st.image(data, caption="Original image")
    quality = assess_image_quality(data)
    st.subheader("Quality assessment"); st.metric("Quality score", f"{quality['quality_score']:.0%}")
    (st.success if quality["is_acceptable"] else st.warning)("Acceptable for analysis" if quality["is_acceptable"] else "Quality issues found")
    for issue in quality["issues"]: st.caption(f"• {issue}")
    if st.button("Run YOLO detection"):
        try:
            result = YoloDetector().detect(data)
            st.write(f"Detected objects: {result['num_detections']}")
            st.dataframe(result["detections"], use_container_width=True)
            st.image(visualize_detections(data, result["detections"]), caption="YOLO detections")
        except RuntimeError as exc: st.error(str(exc))
        except ValueError as exc: st.error(str(exc))
    reference = st.file_uploader("Optional reference image for similarity", type=["jpg", "jpeg", "png", "webp"])
    if reference:
        try:
            result = compare_images(data, reference.getvalue())
            st.subheader("Similarity analysis"); st.metric("Similarity score", f"{result['similarity_score']:.0%}")
            st.info("Similar" if result["is_similar"] else "Not similar")
        except ValueError as exc: st.error(str(exc))
