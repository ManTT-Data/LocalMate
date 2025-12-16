"""
Streamlit Demo for Da Nang RAG System
With Text + Image Search - Uses API endpoints
Run: streamlit run streamlit_demo.py
"""

import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import os

# API Base URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Page config
st.set_page_config(
    page_title="Da Nang Travel RAG",
    page_icon="🏖️",
    layout="wide"
)

# Helper functions
def api_text_search(query: str, max_results: int = 10, rating_min: float = None):
    """Call text search API"""
    try:
        params = {"q": query, "limit": max_results}
        if rating_min and rating_min > 0:
            params["rating_min"] = rating_min
        
        response = requests.get(f"{API_BASE_URL}/search", params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None


def api_category_search(category: str, context: str = None, limit: int = 10):
    """Call category search API"""
    try:
        params = {"limit": limit}
        if context:
            params["context"] = context
        
        response = requests.get(
            f"{API_BASE_URL}/search/category/{category}",
            params=params,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None


def api_image_search(image_bytes: bytes, max_results: int = 10, scene_filter: str = None):
    """Call image search API"""
    try:
        files = {"image": ("image.jpg", image_bytes, "image/jpeg")}
        params = {"max_results": max_results}
        if scene_filter and scene_filter != "All":
            params["scene_filter"] = scene_filter
        
        response = requests.post(
            f"{API_BASE_URL}/search/image",
            files=files,
            params=params,
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None


def api_place_details(place_id: str):
    """Get place details from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/places/{place_id}", timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None


# Header
st.title("🏖️ Da Nang Travel Assistant")
st.markdown("*AI-powered destination recommendations with Text + Image Search*")
st.caption(f"🔗 API: {API_BASE_URL}")

# Tabs
tab1, tab2, tab3 = st.tabs(["🔍 Text Search", "🖼️ Image Search", "🏷️ Category"])

# ===== TAB 1: TEXT SEARCH =====
with tab1:
    st.header("Text Search")
    
    # Sidebar settings (moved to column)
    col1, col2 = st.columns([3, 1])
    
    with col2:
        max_results = st.slider("Max Results", 3, 20, 10, key="text_max")
        rating_min = st.slider("Min Rating", 0.0, 5.0, 0.0, 0.5, key="text_rating")
        
        st.markdown("**💡 Examples:**")
        examples = [
            "quán cafe view đẹp",
            "phở ngon",
            "bánh mì sáng",
            "bar cocktail",
            "hải sản tươi"
        ]
        for ex in examples:
            if st.button(ex, key=f"ex_{ex}", use_container_width=True):
                st.session_state.text_query = ex
    
    with col1:
        query = st.text_input(
            "🔍 Bạn muốn tìm gì?",
            value=st.session_state.get("text_query", ""),
            placeholder="VD: quán cafe view đẹp, phở ngon...",
            key="search_input"
        )
        
        if query:
            with st.spinner("🔄 Đang tìm kiếm..."):
                data = api_text_search(
                    query=query,
                    max_results=max_results,
                    rating_min=rating_min if rating_min > 0 else None
                )
            
            if data and "results" in data:
                results = data["results"]
                st.markdown(f"### 📍 Tìm thấy {len(results)} kết quả")
                
                for i, r in enumerate(results, 1):
                    with st.expander(f"{i}. {r['name']} ({r['category']}) - ⭐{r['rating']}", expanded=i<=3):
                        st.markdown(f"**Score:** {r['score']:.3f} | **Types:** {', '.join(r.get('source_types', [])[:3])}")
                        if r.get('llm_summary'):
                            st.info(r['llm_summary'][:300] + "..." if len(r['llm_summary']) > 300 else r['llm_summary'])
                        elif r.get('description'):
                            st.text(r['description'][:200])
                        
                        # Add button to view details
                        if st.button(f"📍 Xem chi tiết", key=f"detail_{r['place_id']}"):
                            details = api_place_details(r['place_id'])
                            if details:
                                st.json(details)

# ===== TAB 2: IMAGE SEARCH =====
with tab2:
    st.header("🖼️ Tìm kiếm bằng ảnh")
    st.caption("Upload một ảnh để tìm địa điểm tương tự")
    
    uploaded_file = st.file_uploader(
        "Chọn ảnh...",
        type=['jpg', 'jpeg', 'png', 'webp'],
        key="image_upload"
    )
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        max_img_results = st.slider("Max Results", 3, 20, 10, key="img_max")
        scene_filter = st.selectbox(
            "Filter by scene",
            ["All", "food", "interior", "exterior", "view", "people"],
            key="scene"
        )
    
    if uploaded_file is not None:
        # Show uploaded image
        image = Image.open(uploaded_file).convert('RGB')
        col1.image(image, caption="Uploaded Image", width=250)
        
        if st.button("🔍 Search by Image", type="primary"):
            with st.spinner("🔄 Processing image..."):
                # Convert to bytes for API
                img_buffer = BytesIO()
                image.save(img_buffer, format='JPEG')
                image_bytes = img_buffer.getvalue()
                
                data = api_image_search(
                    image_bytes=image_bytes,
                    max_results=max_img_results,
                    scene_filter=scene_filter if scene_filter != "All" else None
                )
            
            if data and "results" in data:
                results = data["results"]
                
                with col2:
                    st.markdown(f"### 📍 Tìm thấy {len(results)} địa điểm tương tự")
                    
                    for i, r in enumerate(results, 1):
                        st.markdown(f"""
                        **{i}. {r['name']}**  
                        📂 {r['category']} | ⭐ {r['rating']} | Score: {r['similarity']:.3f}  
                        🎯 {r['matched_images']} matching images | Scene: {r['scene_type']}
                        """)
                        
                        # View details button
                        if st.button(f"📍 Chi tiết", key=f"img_detail_{r['place_id']}"):
                            details = api_place_details(r['place_id'])
                            if details:
                                st.json(details)
                        
                        st.markdown("---")

# ===== TAB 3: CATEGORY SEARCH =====
with tab3:
    st.header("🏷️ Tìm theo danh mục")
    
    categories = {
        "☕ Cafe": ("cafe", "view đẹp chill"),
        "🍜 Phở": ("pho", "ngon"),
        "🥖 Bánh mì": ("banh_mi", "sáng"),
        "🦐 Hải sản": ("seafood", "tươi ngon"),
        "🍸 Bar": ("bar", "cocktail"),
        "🏨 Hotel": ("hotel", "đẹp")
    }
    
    cols = st.columns(3)
    for i, (label, (cat, context)) in enumerate(categories.items()):
        with cols[i % 3]:
            if st.button(label, use_container_width=True, key=f"cat_{cat}"):
                data = api_category_search(cat, context, 8)
                if data and "results" in data:
                    st.session_state.cat_results = data["results"]
                    st.session_state.cat_name = label
    
    if 'cat_results' in st.session_state and st.session_state.cat_results:
        st.markdown(f"### {st.session_state.cat_name}")
        for i, r in enumerate(st.session_state.cat_results, 1):
            st.markdown(f"{i}. **{r['name']}** ({r['category']}) - ⭐{r['rating']}")

# Footer
st.markdown("---")
st.caption("Built with Gemini Embeddings + SigLIP + Supabase pgvector")
st.caption("Powered by Da Nang Tourism RAG API")
