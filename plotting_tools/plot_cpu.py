import pathlib

import pandas as pandas
import plotly.express as px
import plotly.graph_objects as go
from kaleido.scopes.plotly import PlotlyScope
scope = PlotlyScope()
import os
# Plots the tick over time for all servers in one iteration

template = "plotly_white"

root = pathlib.Path(os.path.abspath(__file__)).parent.absolute()
assert root.is_dir()
output_dir = root
current_server = None

# Change this based on environment!
num_cores=2

# Populate a dataframe from all servers
df = pandas.DataFrame(columns = ["server","iteration","timestamp","cpu"])
fig_line = go.Figure()
servers = []
server_num = 0


for server_dir in os.listdir('../results/'):
    if os.path.isdir(server_dir):
        current_server = server_dir
        servers.append(current_server)
        # For only one iteration
        iteration_dir = server_dir + "/0"

        for data_file in os.listdir(iteration_dir):
            if not os.path.isdir(data_file) and data_file.startswith("sys_metrics"):
                data_path = root.joinpath(iteration_dir).joinpath(data_file)

                iteration_df = pandas.read_csv(data_path, sep="\t")
                #iteration_df.rename(columns = {' tickTime':'tickTime'}, inplace = True)
                #iteration_df.drop(iteration_df.columns[2],axis = 1,inplace = True)
                iteration_df['server'] = current_server
                iteration_df['iteration'] = '0'
                iteration_df['timestamp'] = iteration_df['timestamp'].transform(lambda x: x - x.min())
                iteration_df['timestamp'] = iteration_df['timestamp'].transform(lambda x: x / 1000) # To Seconds

                iteration_df['timestamp'] = iteration_df['timestamp'].transform(lambda x: x - 28) # Took a few seconds for players to join
                iteration_df = iteration_df[iteration_df["timestamp"] >= 0]
                #iteration_df = iteration_df[iteration_df["timestamp"] <= 275] # Don't count player logging out
                #iteration_df['tickTime'] = iteration_df['tickTime'].transform(lambda x: x / 1000000) # To MS
                #iteration_df = iteration_df[(iteration_df["tickTime"] >= 0)]
                #subset = df[(df["Sales Budget"]>30000)]
                iteration_df["proc.cpu_percent"] = iteration_df["proc.cpu_percent"].transform(lambda x: x/(num_cores * 100))
                iteration_df['rolling'] = iteration_df['proc.cpu_percent'].rolling(5).mean() # Mean of 2.5 sec


                df = df.append(iteration_df, ignore_index = True)

                curr_color = "red"
                line_type = dict(color=curr_color,width=2)
                symbol = "diamond"
                if server_num == 1:
                    curr_color="blue"
                    line_type = dict(color=curr_color,width=2)
                    symbol = "circle"
                elif server_num == 2:
                    curr_color="green"
                    line_type = dict(color=curr_color,width=2)
                    symbol = "square"
                server_num +=1
                fig_line.add_trace(go.Scatter(x=iteration_df["timestamp"],y=iteration_df["rolling"], line=line_type, name=current_server, line_shape="spline"))


fig_line.update_layout(legend=dict(y=1,font_size=16),width = 800, height= 400, margin = dict(l=10,r=10,b=10,t=10,pad=0), xaxis_title="time [s]", yaxis_title="CPU percent", font=dict(size=16))


with open(str(output_dir.joinpath("cpu_line.pdf")), "wb") as f:
    f.write(scope.transform(fig_line, format="pdf"))

fig_violin= go.Figure()
server_num = 0

for server in servers:
    curr_color = "red"
    curr_line_color="darkred"
    if server_num == 1:
        curr_color = "blue"
        curr_line_color="darkblue"
    elif server_num == 2:
        curr_color = "green"
        curr_line_color="darkgreen"
    elif server_num > 2:
        # For more than 3 servers, let default colors take over
        fig_violin.add_trace(go.Violin(x=df['server'][df['server'] == server],
                            y=df["proc.cpu_percent"][df['server'] == server],
                            name=server,
                            box_visible=True,
                            meanline_visible=True))
        continue

    server_num += 1

    fig_violin.add_trace(go.Violin(x=df['server'][df['server'] == server],
                            y=df["proc.cpu_percent"][df['server'] == server],
                            name=server,
                            box_visible=True,
                            line_color=curr_line_color,
                            fillcolor=curr_color,
                            points='outliers',
                            meanline_visible=True))
fig_violin.update_traces(showlegend=False)
fig_violin.update_layout(yaxis_title="CPU percent",width = 800, height= 400, margin = dict(l=10,r=10,b=10,t=10,pad=0), font=dict(size=16))


with open(str(output_dir.joinpath("cpu_violin.pdf")), "wb") as f:
    f.write(scope.transform(fig_violin, format="pdf"))
                


