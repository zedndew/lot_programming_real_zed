# Plotting dengan gaya "Clean White"
        fig = go.Figure()

        # Tambah garisan polygon
        fig.add_trace(go.Scatter(
            x=closed_df['E'], 
            y=closed_df['N'],
            mode='lines+markers+text',
            fill="toself",
            fillcolor="rgba(135, 206, 250, 0.3)", # Warna biru cair transparan
            line=dict(color="black", width=2),
            marker=dict(size=8, color="red"),
            text=closed_df['STN'],
            textposition="top center",
            hoverinfo='text+x+y'
        ))

        fig.update_layout(
            plot_bgcolor='white',  # Set latar belakang putih
            paper_bgcolor='white',
            xaxis=dict(
                showgrid=True, 
                gridcolor='lightgrey', 
                zeroline=False,
                scaleanchor="y", # Kunci nisbah paksi X kepada Y
                scaleratio=1
            ),
            yaxis=dict(
                showgrid=True, 
                gridcolor='lightgrey', 
                zeroline=False
            ),
            width=700,
            height=700,
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)