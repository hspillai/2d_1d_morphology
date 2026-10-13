import os
import numpy as np
import pandas as pd

class CustomData:
    def __init__(self, pandas_path, checkpoint_txt_name = 'checkpoint.txt',
                 df_pickle_name = 'DataFrame.pickle',
                 columns = None):
        
        self.data = []
        self.entries_processed = set()
        self.pandas_path = pandas_path
        self.checkpoint_filename = self.pandas_path + checkpoint_txt_name#'checkpoint.txt'
        self.pandas_filename = self.pandas_path + df_pickle_name #'DataFrame.pickle'
    
        # Default columns if not provided
        if columns is None:
            self.columns = ['mesh', 'rho', 'R','ipd',
                            'r', 'L', 'sel', 'converged',
                            'resolution']
        else:
            self.columns = columns

        self.df = pd.DataFrame(columns =self.columns)            
        # Load checkpoint and dataframe
        self.load_checkpoint()
        self.load_dataframe()

    def load_checkpoint(self):
        if os.path.exists(self.checkpoint_filename):
            with open(self.checkpoint_filename, 'r') as f:
                self.entries_processed = set(line.strip() for line in f)                
                # for line in f:
                #     self.entries_processed.add(line.split('\n')[0])            

    def load_dataframe(self):
        if os.path.exists(self.pandas_filename):
            print(f'Reading existing data from: {self.pandas_filename}')
            self.df = pd.read_pickle(self.pandas_filename)

    def entry_exists(self, mesh_path):
        return mesh_path in self.entries_processed

    def add_entry(self, row_dict, ignore_check = False):
        mesh_path = row_dict['mesh']        
        if ignore_check == True:
            self.entries_processed.add(mesh_path)
            self.df = pd.concat([self.df, pd.DataFrame([row_dict])], ignore_index=True)            
        else:
            existing_idx = self.df[self.df['mesh'] == mesh_path].index
            if not existing_idx.empty:
                print(f"Overwriting existing entry for mesh: {mesh_path}")
                self.df.loc[existing_idx[0]] = row_dict  # Overwrite in-place
            else:
                self.df = pd.concat([self.df, pd.DataFrame([row_dict])], ignore_index=True)
                self.entries_processed.add(mesh_path)                
            # if mesh_path in self.entries_processed:
            #     print(f"Skipping already processed mesh: {mesh_path}")
            #     return
            
#            self.df = pd.concat([self.df, pd.DataFrame([row_dict])], ignore_index=True)

    def save_checkpoint(self):
        with open(self.checkpoint_filename, 'w') as f:
            for entry in sorted(self.entries_processed):
                f.write(entry + '\n')

    def save_dataframe(self):
        self.df.to_pickle(self.pandas_filename)

    def save_all(self):
        self.save_dataframe()
        self.save_checkpoint()
        
    def filter_data(self, columns = None, **kwargs):
        """
        Filter the DataFrame based on the specified column(s) and value(s).

        Parameters:
        - columns: List of column names to include in the output DataFrame (optional).
        - **kwargs: Keyword arguments specifying the column(s) to filter on and their corresponding value(s).

        Returns:
        - filtered_df: The filtered DataFrame.
        """
        filtered_df = self.df
        print(kwargs.items())
        for column, value in kwargs.items():

            if column in ['Electrode_Potential', 'length', 'active_site_width', 'ipd/L']:
                filtered_df = filtered_df[np.isclose(filtered_df[column], value)]
            else:
                filtered_df = filtered_df[filtered_df[column] == value]

        if columns is not None:
            filtered_df = filtered_df[columns]

        return filtered_df

    def remove_non_converged(self, ignore_meshes=None,
                             verbose = True):
        """
        ignore_meshes: list or set, optional
        mesh names to keep even if converged == False.

        vebose: bool
        print information about removed entries
        """

        if ignore_meshes is None:
            ignore_meshes = set()
        else:
            ignore_meshes = set(ignore_meshes)

        if 'converged' not in self.df.columns:
            raise KeyError("Column converged not found in dataframe")

        mask_drop = (self.df['converged'] == False) & (~self.df['mesh'].isin(ignore_meshes))
        rows_to_drop = self.df[mask_drop]

        if rows_to_drop.empty:
            if verbose:
                print("all entries are converged.")
            return self

        meshes_to_remove = rows_to_drop['mesh'].tolist()

        if verbose:
            print(f"Removing {len(meshes_to_remove)} non-converged entries:")
            for m in meshes_to_remove:
                print(f"  - {m}")

        # Remove from entries_processed
        for mesh in meshes_to_remove:
            self.entries_processed.discard(mesh)  # discard avoids KeyError

        # Drop from dataframe
        self.df = self.df.drop(rows_to_drop.index).reset_index(drop=True)

        return self
    # def clear_nc(self, ignore_names = []):
    #     """
    #     check if we have any non-converged and clear them from the df and entries_processed. 
    #     additional option to potentially ignore in some cases 
    #     """
        
    #     self.df_nc = self.df[self.df['Converged_2D'] == False]
    #     dropped_inxs = np.array(self.df_nc.index) # the indexs we want to drop
    #     inxs_not_drop = np.array(self.df[self.df['meshFileName'].isin(ignore_names)].index.astype(int))
    #     print('dropped_inxs: ', dropped_inxs)
    #     print('inxs_not_drop: ', inxs_not_drop)

    #     self.dropped_inxs = np.delete(dropped_inxs, np.searchsorted(dropped_inxs, np.intersect1d(dropped_inxs, inxs_not_drop)))

    #     if len(self.dropped_inxs) > 0:            
    #         print('there are some left to converge. Removing from the entries processed and dataframe.')
    #         for i in self.df_nc['id'].values:
    #             if self.df_nc[self.df_nc['id'] == i]['meshFileName'].values[0] in ignore_names:
    #                 # find index of self.df_nc[self.df_nc['id'] == i]
    #                 print('We are not ignoring this!')
    #             else:
    #                 print(i)
    #                 print('removed')
    #                 try:
    #                     self.entries_processed.remove(i)
    #                 except KeyError:
    #                     print('#')

    #         self.df = self.df.drop(self.dropped_inxs) # this should be changed             
    #     else:
    #         print('All are converged.')

    def remove_converged_ones(self, converged_names = []):
        # remove certain convergeds ones helpful in certain situations
        converged_rows = self.df[self.df['meshFileName'].isin(converged_names)]
#        for i in converged_names:
        inxs = []
        for i in converged_rows.iterrows():
            inx = i[0]
            id = i[1]['id']
            inxs.append(inx)
            try:
                self.entries_processed.remove(id)
            except KeyError:
                print('#')

        self.df = self.df.drop(inxs) # this should be changed


    def scale_column(self, col, factor):
        if col in self.df.columns:
            self.df[col] *= factor
        else:
            raise KeyError(f"Column '{col}' not found in dataframe")
        return self

    def sort_by(self, col, ascending=True):
        if col in self.df.columns:
            self.df = self.df.sort_values(col, ascending=ascending)
        else:
            raise KeyError(f"Column '{col}' not found in dataframe")
        return self

    def add_ratio_column(self, new_col, num_col, denom_col):
        if num_col in self.df.columns and denom_col in self.df.columns:
            self.df[new_col] = self.df[num_col] / self.df[denom_col]
        else:
            raise KeyError(f"Required columns '{num_col}' or '{denom_col}' not found")
        return self

    def difference_columns(self, new_col, col_1, col_2):
        if col_1 in self.df.columns and col_2 in self.df.columns:
            self.df[new_col] = self.df[col_1]  - self.df[col_2]
        else:
            raise KeyError(f"Required columns '{col_1}' or '{col_2}' not found")
        return self

    def calculate_loading(self, density = 8.96):
        '''
        density is the density used in g/cm3, default is the 8.96 (for Cu)
        '''
        self.df['loading(cm)'] = self.df['rho'] * (1/3) * np.sqrt(self.df['rho']/2) * self.df['R'] * (100)
        self.df['loading(mg/cm2)'] = self.df['loading(cm)'] * density * 1000    
        return self
