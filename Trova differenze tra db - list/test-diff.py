import pandas as pd

df_curr = pd.read_csv('Current.csv', sep=';')
df_back = pd.read_csv('Backup.csv', sep=';')

added = df_curr[~df_curr.iloc[:, 2].isin(df_back.iloc[:, 2])]
removed = df_back[~df_back.iloc[:, 2].isin(df_curr.iloc[:, 2])]
mod = df_curr[df_curr.iloc[:, 2].isin(df_back.iloc[:, 2])]

mod_info = pd.DataFrame(columns=mod.columns)
mod_delta = pd.DataFrame(columns=['Delta'])  #Nuovo-Vecchio

for row in range(mod.shape[0]):
    art = mod.iloc[row, 2]
    num_curr = mod.iloc[row, 3]
    num_back = df_back[df_back.iloc[:, 2] == art].iloc[0, 3]
    if num_curr != num_back:
        mod_info = mod_info._append(mod.iloc[[row]], ignore_index=True)
        mod_delta = mod_delta._append(pd.DataFrame({'Delta': [num_curr - num_back]}), ignore_index=True)

mod_res = pd.concat([mod_info, mod_delta], axis=1)

print(df_back)
print(df_curr)
print(added)
print(removed)
print(mod_info)
print(mod_delta)
print(mod_res)