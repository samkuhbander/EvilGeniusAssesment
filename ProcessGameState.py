import pandas as pd
import os
import matplotlib.path as mplPath
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from functools import lru_cache

class ProcessGameState:

    def __init__(self, filepath):
        if not os.path.isfile(filepath):
            raise ValueError(f"File {filepath} does not exist.")
        self.filepath = filepath
        self.data_frame = None

    def load_data(self):
        self.data_frame = pd.read_parquet(self.filepath, engine='pyarrow')

    def clean_data(self):
        self.data_frame.dropna(inplace=True)

    def check_boundaries(self, boundary_area):
        xy_boundary = boundary_area.get('XY')
        z_bounds = boundary_area.get('Z')

        # Check if x, y coordinates are within the XY boundary
        in_xy_boundary = xy_boundary.contains_points(self.data_frame[['x', 'y']].values)

        # Check if z coordinates are within the Z boundary
        in_z_boundary = (z_bounds[0] <= self.data_frame['z']) & (self.data_frame['z'] <= z_bounds[1])

        # Create a new column 'In_Boundary' to store the result of boundary checks
        self.data_frame['In_Boundary'] = in_xy_boundary & in_z_boundary.values

    def extract_weapon_classes(self):
        # Assuming 'inventory' is the column name where your JSON data is stored
        if 'inventory' not in self.data_frame.columns:
            raise ValueError("No inventory column found.")

        # Extract weapon classes
        weapon_classes = set()
        for inventory in self.data_frame['inventory']:
            for item in inventory:
                weapon_classes.add(item.get('weapon_class', None))  # add None default to handle missing 'weapon_class'

        # Return unique weapon classes
        return list(weapon_classes)

    def extract_area_names(self):
        if 'area_name' not in self.data_frame.columns:
            raise ValueError("No area_name column found.")
        
        # Extract area names
        area_names = set()
        for area_name in self.data_frame['area_name']:
            area_names.add(area_name)

        # Return unique area names
        return list(area_names)

    def player_has_rifle_or_smg(self, player_row):
        for item in player_row['inventory']:
            if item.get('weapon_class') in ['Rifle', 'SMG']:
                return True
        return False

    def process(self, boundary_area):
        self.load_data()
        if self.data_frame is None:
            raise ValueError("No data to clean. Load data first.")
        self.clean_data()
        self.check_boundaries(boundary_area)
        weapon_classes = self.extract_weapon_classes()
        area_names = self.extract_area_names()
        print(f"Found {len(weapon_classes)} weapon classes: {weapon_classes}")
        print(f"Found {len(area_names)} area names: {area_names}")

    def average_entry_time(self, team, side, area_name, min_weapons):
        # Filter data for given team, side, and area name
        team_data = self.data_frame[(self.data_frame['team'] == team) 
                                     & (self.data_frame['side'] == side) 
                                     & (self.data_frame['area_name'] == area_name)].copy()  # Create a copy here

        #Convert clock_time from str 'MM:SS' to int seconds
        team_data['clock_time'] = team_data['clock_time'].apply(lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1]))
        
        # Group by time and filter for groups with multiple unique players
        multi_player_data = team_data.groupby(['clock_time']).filter(lambda x: x['player'].nunique() >= min_weapons)

        # Remove any player that does not have a rifle or SMG
        multi_player_data = multi_player_data[multi_player_data.apply(self.player_has_rifle_or_smg, axis=1)]

        #Remove rows where bomb is planted because seconds will reset to 0
        multi_player_data = multi_player_data[multi_player_data['bomb_planted'] == False]

        # Find the lowest time per round and add it to find the average
        multi_player_data = multi_player_data.groupby(['round_num', 'area_name'])['clock_time'].min().reset_index()

        # Calculate the mean of clock_time (in seconds)
        average_seconds = multi_player_data['clock_time'].mean()

        # Convert the average time back to MM:SS format
        minutes, seconds = divmod(average_seconds, 60)

        #Check if average time is not a number
        if np.isnan(minutes) or np.isnan(seconds):
            return 'No average time found'

        average_time_MM_SS = f"{int(minutes):02}:{int(seconds):02}"

        return average_time_MM_SS

    def plot_heatmap_on_map(self, img_path, area_name, team, side):

        extent = [-2650, 2650, -2650, 2650]
        shift_x = 2190
        shift_y = 890
            
        # Create a new figure
        fig, ax = plt.subplots(figsize=(8, 6))

        # Load and show the image of the map on the plot
        ax.imshow(plt.imread(img_path), extent=extent)

        # Filter the data for the given team, side, and area name
        area_data = self.data_frame[(self.data_frame['team'] == team )
                                        & (self.data_frame['side'] == side)
                                        & (self.data_frame['area_name'] == area_name)].copy()

        area_data['x'] += shift_x
        area_data['y'] += shift_y

        # Plot the data as a heatmap
        sns.kdeplot(x=area_data['x'], y=area_data['y'], cmap="Reds", fill=True, alpha=0.5, ax=ax, thresh=0.4)

        # Define the bounds of your heatmap 
        xmin, xmax = area_data['x'].min(), area_data['x'].max()
        ymin, ymax = area_data['y'].min(), area_data['y'].max()

        # Add a bit of padding around the heatmap for visual clarity
        padding = 450  # adjust this value based on your data and preference
        plt.xlim(xmin - padding, xmax + padding)
        plt.ylim(ymin - padding, ymax + padding)
        plt.title(f"{team} {side} {area_name} Heatmap")

        # Show the plot
        plt.show()

    def entry_frequency(self, team, side):
        # Filter data for given team and side
        team_data = self.data_frame[(self.data_frame['team'] == team) 
                                    & (self.data_frame['side'] == side)]
        # Group by round
        round_groups = team_data.groupby('round_num')

        # Check if any entry in each round group is within the boundary
        rounds_with_boundary_entry = round_groups['In_Boundary'].any()

        # Calculate the frequency
        frequency = rounds_with_boundary_entry.sum() / len(round_groups)

        return frequency

# Define light blue area choke point
light_blue_area = {
    'Z': (285, 421),
    'XY': mplPath.Path([[-1735, 250], [-2024, 398], [-2806, 742], [-2472, 1233], [-1565, 580]])
}

# Create an instance of ProcessGameState and process the game state data
game_state_processor = ProcessGameState('data/game_state_frame_data.parquet')
game_state_processor.process(light_blue_area)

# Calculate entry frequency for Team2 on T side
entry_frequency = game_state_processor.entry_frequency('Team2', 'T')
print(f"Frequency of Team2 entering light blue boundary on T side: {entry_frequency * 100:.2f}%")

# Print the average timer for Team2 on T side entering BombsiteB with at least 2 weapons
average_time = game_state_processor.average_entry_time('Team2', 'T', 'BombsiteB', 2)
print(f"Average timer for Team2 entering light blue boundary on T side: {average_time}")

#Heatmap of Team2 on CT side entering BombsiteB
game_state_processor.plot_heatmap_on_map('map/de_overpass_radar.jpeg', 'BombsiteB', "Team2", "CT")
