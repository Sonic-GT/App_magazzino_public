import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime, timedelta

# current_date = str(datetime.now().date())
past_date = str((datetime.now() - timedelta(days=1)).date())
file_path = "Backups/"

gp = gspread.service_account(filename='trova-differenze-chiave.json')
gsheet = gp.open('Magazzino')
wsheet = gsheet.worksheet('Foglio1').get_all_records()

df = pd.DataFrame(wsheet)
df['AGGIORNATO'] = [past_date] + [''] * (len(df) - 1)

# Copia su file
df.to_csv(file_path + past_date + ".csv", sep=";", index=False)

# Copia su drive
backup_wsheet = gp.open('Backup_precedente').worksheet('Foglio1')
backup_wsheet.update([df.columns.values.tolist()] + df.values.tolist())
