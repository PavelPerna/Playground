import plotly.graph_objects as go

# Define vertices for K_{3,3}: 3 on one side (A, B, C), 3 on the other (X, Y, Z)
vertices = [(0.2, 0.2, 0.2), (0.2, 0.8, 0.2), (0.8, 0.2, 0.2), (0.8, 0.8, 0.8), (0.8, 0.2, 0.8), (0.2, 0.8, 0.8)]
x, y, z = zip(*vertices)

# Define edges (A-X, A-Y, A-Z, B-X, B-Y, B-Z, C-X, C-Y, C-Z)
edges = [
    (0, 3), (0, 4), (0, 5), (1, 3), (1, 4), (1, 5),
    (2, 3), (2, 4), (2, 5)
]
edge_x, edge_y, edge_z = [], [], []
for edge in edges:
    x0, y0, z0 = vertices[edge[0]]
    x1, y1, z1 = vertices[edge[1]]
    edge_x.extend([x0, x1, None])
    edge_y.extend([y0, y1, None])
    edge_z.extend([z0, z1, None])

# Plot
fig = go.Figure(data=[
    go.Scatter3d(x=edge_x, y=edge_y, z=edge_z, mode='lines', line=dict(color='purple', width=2)),
    go.Scatter3d(x=x, y=y, z=z, mode='markers', marker=dict(size=5, color='red'))
])
fig.update_layout(scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'), width=700, margin=dict(r=0, b=0, l=0, t=0))
fig.show()

vertices = [(0.2, 0.2, 0.2), (0.2, 0.8, 0.2), (0.8, 0.2, 0.2), (0.8, 0.8, 0.8), (0.8, 0.2, 0.8), (0.2, 0.8, 0.8)]

# Add movement vectors (example offsets)
mov_vectors = [(0., 0, 1), (0, 1, 0), (1, 0, 0), (1,1,1), (1, 0, 1), (0, 1,1)]
mov_x, mov_y, mov_z = [], [], []
for v, mov in zip(vertices, mov_vectors):
    x0, y0, z0 = v
    x1, y1, z1 = x0 + mov[0], y0 + mov[1], z0 + mov[2]
    mov_x.extend([x0, x1, None])
    mov_y.extend([y0, y1, None])
    mov_z.extend([z0, z1, None])

fig.add_trace(go.Scatter3d(x=mov_x, y=mov_y, z=mov_z, mode='lines', line=dict(color='orange', width=2), name='Movement'))

fig.add_trace(go.Scatter3d(x=[v[0] for v in vertices], y=[v[1] for v in vertices], z=[v[2] for v in vertices],
                           mode='text', text=[f"{v[0]:.1f}{v[1]:.1f}{v[2]:.1f}" for v in vertices],
                           textposition="top center"))
fig.update_layout()
fig.write_html("p.html")