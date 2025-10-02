# SIMPLIFIED STEP 4: Content Brief
# This replaces lines 3043-3474 in app.py

# Copy this code to replace the old Step 4

elif st.session_state.current_step == 4:
    st.subheader("Step 4: Content Brief")

    # Check if we have approved structure from Step 3
    if not st.session_state.optimization_data.get('structure_approved'):
        st.warning("⚠️ Please complete structure review in Step 3 first")
        if st.button("← Back to Review Structure"):
            st.session_state.current_step = 3
            st.rerun()
    else:
        # Load section functions for content generation
        section_functions = load_section_functions()
        function_options = get_function_options(section_functions)
        parsed = st.session_state.optimization_data.get('parsed_structure', {})

        # Get approved structure from Step 3
        approved_structure = st.session_state.optimization_data.get('approved_structure', [])

        # Initialize optimized_headings from approved_structure if not already done
        if 'optimized_headings' not in st.session_state.optimization_data:
            optimized_headings = []
            analysis_result = st.session_state.optimization_data.get('analysis_result', {})
            recommendations = analysis_result.get('recommendations', [])

            for item in approved_structure:
                action = item['action']
                heading = item['heading']

                # Find matching recommendation for additional data
                matching_rec = next((r for r in recommendations if r['heading'] == heading), None)

                heading_dict = {
                    'level': 'H2',
                    'text': heading,
                    'original_text': heading if action in ['keep', 'improve'] else '',
                    'action': action,
                    'function': auto_detect_function(heading, section_functions),
                    'h3_subheadings': matching_rec.get('h3_subheadings', []) if matching_rec else [],
                    'reason': matching_rec.get('reason', '') if matching_rec else ''
                }

                # For keep/improve actions, find original content
                if action in ['keep', 'improve']:
                    original_content = ''
                    existing_structure = analysis_result.get('existing_structure', {})

                    for existing_h in existing_structure.get('headings', []):
                        # Flexible matching
                        if (existing_h['text'].lower() in heading.lower() or
                            heading.lower() in existing_h['text'].lower()):
                            original_content = parsed.get('sections', {}).get(existing_h['text'], '')
                            break

                    heading_dict['original_content'] = original_content
                    heading_dict['word_count'] = len(original_content.split()) if original_content else 0
                else:
                    # ADD action
                    heading_dict['original_content'] = ''
                    heading_dict['word_count'] = 0

                optimized_headings.append(heading_dict)

            st.session_state.optimization_data['optimized_headings'] = optimized_headings
            st.success(f"✅ Loaded {len(optimized_headings)} sections from approved structure!")

        # Display brief summary
        st.info("📝 **Finalize your content brief** by selecting the function for each section")

        # Summary metrics
        optimized_headings = st.session_state.optimization_data['optimized_headings']
        keep_count = len([h for h in optimized_headings if h.get('action') == 'keep'])
        improve_count = len([h for h in optimized_headings if h.get('action') == 'improve'])
        add_count = len([h for h in optimized_headings if h.get('action') == 'add'])

        st.markdown(f"**{keep_count} Keep** | **{improve_count} Improve** | **{add_count} Add** = **{len(optimized_headings)} Total Sections**")

        st.markdown("---")

        # Display each heading with function selector (read-only action badge)
        for i, heading in enumerate(optimized_headings):
            action = heading.get('action', 'keep')
            heading_text = heading['text']
            word_count = heading.get('word_count', 0)

            # Action emoji and color
            action_emoji = {"keep": "✅", "improve": "🔧", "add": "➕"}
            action_label = {"keep": "Keep", "improve": "Improve", "add": "Add"}

            col1, col2, col3 = st.columns([3, 2, 1])

            with col1:
                st.markdown(f"**{i+1}. {heading_text}**")
                st.caption(f"{action_emoji.get(action, '•')} {action_label.get(action, action).upper()} • {word_count} words")

            with col2:
                # Function selector
                current_function = heading.get('function', 'general')
                selected_function = st.selectbox(
                    f"Function for section {i+1}",
                    options=list(function_options.keys()),
                    format_func=lambda x: function_options[x],
                    index=list(function_options.keys()).index(current_function) if current_function in function_options else 0,
                    key=f"func_{i}",
                    label_visibility="collapsed"
                )
                heading['function'] = selected_function

            with col3:
                st.write("")  # Spacing

        # CTA Product Selection
        st.markdown("---")
        with st.expander("🎯 CTA Product Settings", expanded=False):
            st.markdown("**Configure product CTAs for optimized content**")

            if APIS_AVAILABLE:
                try:
                    from core.product_loader import product_loader

                    # Get available products
                    products = product_loader.get_products()
                    product_options = {"none": "No Product CTA"}
                    for product in products:
                        product_options[product['slug']] = f"{product['name']} - {product['category']}"

                    selected_product = st.selectbox(
                        "Select Product for CTA",
                        options=list(product_options.keys()),
                        format_func=lambda x: product_options[x],
                        index=0,
                        key="opt_product_select"
                    )

                    st.session_state.optimization_data['selected_product'] = selected_product

                    if selected_product != "none":
                        product_data = next((p for p in products if p['slug'] == selected_product), None)
                        if product_data:
                            st.info(f"**{product_data['name']}**\n\n{product_data['description'][:200]}...")
                except Exception as e:
                    st.warning(f"Could not load products: {str(e)}")
                    st.session_state.optimization_data['selected_product'] = "none"
            else:
                st.warning("API not available. Product CTAs disabled.")
                st.session_state.optimization_data['selected_product'] = "none"

        # Navigation
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("← Back to Review Structure"):
                st.session_state.current_step = 3
                st.rerun()
        with col3:
            if st.button("Continue to Generate →", type="primary"):
                st.session_state.current_step = 5  # Now goes to Step 5 (Generate)
                st.rerun()
