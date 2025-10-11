import streamlit as st
import pandas as pd
import time
from components.sidebar import render_sidebar
from services.backend_api import (
	get_data_sources,
	add_data_source,
	delete_data_source,
	reindex_knowledge_base,
	update_data_source
)

st.set_page_config(page_title="Knowledge Base", page_icon="📚", layout="wide")

# Render sidebar
render_sidebar()

st.title("📚 Knowledge Base Management")

# --- Chức năng 1: Form nhập liệu ---
with st.expander("➕ Add New Knowledge Source", expanded=False):
	st.subheader("Enter Information")

	if "form_errors" not in st.session_state:
		st.session_state.form_errors = {}

	st.markdown("**Title**", unsafe_allow_html=True)
	title = st.text_input("Title", key="form_title_input", label_visibility="collapsed")
	if "title" in st.session_state.form_errors:
		st.error(st.session_state.form_errors["title"])

	st.markdown("**Short Description**")
	description = st.text_area("Short Description", key="form_description_input", label_visibility="collapsed")

	st.markdown("**Source Type**")
	source_type = st.radio("Source Type:", ("Upload File", "Enter Website URL"), horizontal=True,
						   key="source_type_radio", label_visibility="collapsed")

	uploaded_file, url_input = None, None
	if source_type == "Upload File":
		uploaded_file = st.file_uploader("Choose .txt or .pdf files", type=['pdf', 'txt'], key="form_file_uploader")
		if "file" in st.session_state.form_errors:
			st.error(st.session_state.form_errors["file"])
	else:
		url_input = st.text_input("Enter the website URL", key="form_url_input")
		if "url" in st.session_state.form_errors:
			st.error(st.session_state.form_errors["url"])

	if st.button("Add to Knowledge Base"):
		st.session_state.form_errors = {}
		is_valid = True
		if not title:
			st.session_state.form_errors["title"] = "Title is required!"
			is_valid = False
		if source_type == "Upload File" and not uploaded_file:
			st.session_state.form_errors["file"] = "Please upload a file!"
			is_valid = False
		if source_type == "Enter Website URL" and not url_input:
			st.session_state.form_errors["url"] = "Please enter a URL!"
			is_valid = False

		if is_valid:
			file_data = (uploaded_file.name, uploaded_file.getvalue()) if uploaded_file else None
			with st.spinner("Processing..."):
				success, message = add_data_source(title, description, url_input, file_data)
				if success:
					st.toast(message, icon="✅")
					if 'current_data' in st.session_state: del st.session_state.current_data
					time.sleep(1)
				else:
					st.error(message)
		st.rerun()

st.markdown("---")
st.header("List of Knowledge Sources")

# --- HÀNG NÚT HÀNH ĐỘNG ---
col1, col2, _ = st.columns([1.5, 2, 6.5])
with col1:
	if st.button("🔄 Reload List"):
		if 'current_data' in st.session_state: del st.session_state.current_data
		st.rerun()
with col2:
	if st.button("⚙️ Update Knowledge"):
		st.session_state.reindexing = True

# --- Xử lý trạng thái re-indexing ---
if 'reindexing' in st.session_state and st.session_state.reindexing:
	with st.info("⏳ Updating knowledge base... Please wait."):
		success, message = reindex_knowledge_base()
		if success:
			st.success(message)
		else:
			st.error(message)
		del st.session_state.reindexing
		if 'current_data' in st.session_state: del st.session_state.current_data
		time.sleep(2)
		st.rerun()

# --- Tải dữ liệu ---
if 'page' not in st.session_state: st.session_state.page = 1
if 'current_data' not in st.session_state:
	st.session_state.current_data = get_data_sources(page=st.session_state.page)

data = st.session_state.current_data
sources = data.get("items", [])
total_pages = data.get("total_pages", 1)

# --- HIỂN THỊ PHÂN TRANG (LAYOUT ĐÃ SỬA) ---
if total_pages > 1:
	_, col_prev, col_text, col_next, _ = st.columns([4, 0.6, 2, 0.6, 4])
	with col_prev:
		if st.button("◀️", disabled=(st.session_state.page <= 1)):
			st.session_state.page -= 1
			if "current_data" in st.session_state:
				del st.session_state["current_data"]
			st.rerun()
	with col_text:
		st.markdown(
			f"<p style='text-align: center; font-weight: bold; margin-top: 5px;'>Page {st.session_state.page} / {total_pages}</p>",
			unsafe_allow_html=True)
	with col_next:
		if st.button("▶️", disabled=(st.session_state.page >= total_pages)):
			st.session_state.page += 1
			if "current_data" in st.session_state:
				del st.session_state["current_data"]
			st.rerun()

# --- HIỂN THỊ BẢNG DỮ LIỆU ---
if not sources:
	st.warning("No knowledge sources found.")
else:
	df = pd.DataFrame(sources)
	if 'Select' not in df.columns: df.insert(0, "Select", False)
	st.session_state.original_df = df.copy()

	edited_df = st.data_editor(df, column_config={
		"Select": st.column_config.CheckboxColumn("Select"), "id": None,
		"title": st.column_config.TextColumn("Title", required=True),
		"description": st.column_config.TextColumn("Description", width="large"),
		"source_type": st.column_config.Column("Type", disabled=True),
		"source_name": st.column_config.Column("Source (File/URL)", disabled=True),
		"status": st.column_config.Column("Status", disabled=True),
	}, use_container_width=True, hide_index=True, num_rows="fixed", key="data_editor")

	selected_rows = edited_df[edited_df["Select"]]
	if not selected_rows.empty:
		if st.button("🗑️ Delete Selected Items", type="primary"):
			with st.spinner("Deleting..."):
				for _, row in selected_rows.iterrows():
					delete_data_source(row['id'])
			st.success("Successfully deleted!")
			del st.session_state.current_data
			st.rerun()

	original_data_cols = st.session_state.original_df.drop(columns=['Select'], errors='ignore')
	edited_data_cols = edited_df.drop(columns=['Select'])
	if not original_data_cols.equals(edited_data_cols):
		merged = original_data_cols.merge(edited_data_cols, on='id', how='inner', suffixes=('_orig', '_edited'))
		diffs = merged[
			(merged['title_orig'] != merged['title_edited']) |
			(merged['description_orig'] != merged['description_edited'])
			]
		for _, row in diffs.iterrows():
			source_id = row['id']
			updated_data = {"title": row["title_edited"], "description": row["description_edited"]}
			update_data_source(source_id, updated_data)
		st.toast("Changes saved!")
		del st.session_state.current_data
		st.rerun()
