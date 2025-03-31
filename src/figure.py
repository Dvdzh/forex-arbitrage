import json 
# from st_link_analysis import NodeStyle, EdgeStyle

class Figure():

    def __init__(self):
        pass

    def _series_to_elements(self, prices_series):

        """ Transforme une serie de prix en un dictionnaire de noeuds et d'arcs"""
        # Get the list of currency 
        pairs = prices_series.index
        list_currency = set([ticker[:3] for ticker in pairs.tolist()])

        # Create the nodes and edges
        nodes = [{"data": {"id":ticker, 
                        "label": "CURRENCY",
                        "name": ticker}}  for ticker in list_currency]
        edges = [{"data": {"id":pair,
                        "label": "PAIR_DIRECT" if prices_series.loc[pair] > 1 else "PAIR_INVERSE",
                        "source": pair[:3],
                        "target": pair[3:6], 
                        "rate":f"{prices_series.loc[pair]:.3f}"}} for pair in pairs]
        
        with open(f"data/figure/graph_{prices_series.name}.json", "w") as f:
            json.dump({"nodes": nodes, "edges": edges}, f, indent=4)

        return {"nodes": nodes, "edges": edges}
    
    def get_style(self):
        return [
            NodeStyle("CURRENCY", "#FF7F3E", "name", "currency"),
        ]
    
    def get_edge_style(self):
        return [
            EdgeStyle("PAIR_DIRECT", directed=True, color="#83B256"),
            EdgeStyle("PAIR_INVERSE", directed=True, color="#B29D56"),
        ]

    def get_heatmap(self):
        import plotly.graph_objects as go

        fig = go.Figure()

        fig.add_trace(
            go.Heatmap(
                z=[[1, 2], [3, 4]],
                x=["A", "B"],
                y=["C", "D"],
                colorscale="Viridis",
            )
        )

        fig.update_layout(
            title="Heatmap",
            xaxis_title="X Axis",
            yaxis_title="Y Axis",
        )

        return fig
if __name__ == "__main__":
    # fig = Figure()
    # print("Figure class created.")

    import pandas as pd 

    price_df = pd.read_csv("data/dataloader/prices_temporal.csv", index_col=0, header=0)

    # iterrows
    fig = Figure()
    for index, row in price_df.iterrows():
        print(index)
        print(row)
        fig._series_to_elements(row)