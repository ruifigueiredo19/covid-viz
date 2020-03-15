# IMPORTS
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import datetime
import pickle

# CONSTANTS
class color:
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

    
# COVID DATA
class Data:
    URLS = {
        'confirmed': 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv',
        'deaths': 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv',
        'recovered': 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv'
    }
    
    @classmethod
    def from_pickle(cls, datatype, autosave=False):
        if datatype not in cls.URLS:
            raise ValueError(f"Invalid type received for datatype: '{datatype}'.")
            
        with open(f'{datatype}.pickle', 'rb') as picklefile:
            return pickle.load(picklefile)
    
    
    def __init__(self, datatype='confirmed', from_csv=False):
        if datatype not in self.URLS:
            raise ValueError(f"Invalid type received for datatype: '{datatype}'.")
                  
        self.datatype = datatype
        self.url = self.URLS[self.datatype]
        
        if from_csv:
            print("Waning: Data loaded from csv directly has no datetime associated. Load pickle instead for that information")
            self.datetime = datetime.datetime.now()
            self.df = pd.read_csv(f'{self.datatype}.csv', index_col=0)
            
        else:
            self.df, self.datetime = self.download()
            if autosave:
                self.save()

            
        # Useful vars
        self.dt_columns = [datetime.datetime.strptime(col, "%d/%m/%Y") for col in self.df.columns]
        self.datetime_str = self.datetime.strftime("%d %b %Y, %I:%M:%S%p")
        self.total_cases = self.df.iloc[:,-1].sum()

    
    def download(self):
        # Get time of download and dataframe
        dt = datetime.datetime.utcnow()
        df = pd.read_csv(self.url)
        
        # Fix data
        df.drop(columns=['Lat', 'Long'], inplace=True)
        df = df.groupby(['Country/Region']).sum()
        df.rename(columns=lambda s: '{1}/{0}/20{2}'.format(*(c.zfill(2) for c in s.split('/'))), inplace=True)  # Change format from US to EU   # df.columns = pd.to_datetime(df.columns, format='%m/%d/%y')   #  
        # print("Finished downloading")
        return df, dt
        
    def save(self):
        # Save CSV
        self.df.to_csv(f'{self.datatype}.csv')
        
        # Save Pickle too
        with open(f'{self.datatype}.pickle', 'wb') as picklefile:
            pickle.dump(self, picklefile)
            
        # print("Finished saving")
        
        
    def plot(self, countries=('Portugal', 'Italy', 'Spain'), savefig=False):
        # Formatters
        daily_minor_locator = matplotlib.dates.DayLocator()
        daily_major_locator = matplotlib.dates.DayLocator(interval=7)
        date_formatter = matplotlib.dates.DateFormatter('%d/%m')

        # All plots
        N = len(countries)
        n_rows = round(N/2 + 0.6)  # + 0.6 for proper integer rounding on cases like 2.5
        n_cols = 2
        
        fig, axs = plt.subplots(nrows=n_rows, ncols=n_cols, figsize = (20, 3 * (N+1)), constrained_layout=True)
        plt.suptitle(f'Cases {self.datatype} (World total: {self.total_cases})\n', fontsize=25)
        plt.figtext(.5, .952, f'Generated at: {self.datetime_str} UTC', fontsize=16, ha='center')
        
        total_ax = axs[-1, N % 2]
        total_ax.set_title('All Countries')
        
        if N % 2 == 0:
            axs[-1, -1].remove()
            
        # Plot each of them
        for i, country in enumerate(countries):
            ax = axs[i // 2, i % 2]
            ax.set_title(country)
            ax.plot_date(self.dt_columns, df.loc[country], ls=':', marker='.', c=f'C{i}', label=country)
            total_ax.plot_date(self.dt_columns, df.loc[country], ls=':', marker='.', c=f'C{i}', label=country)

        # Formatting all plots (including total)
        for i in range(N + 1):
            ax = axs[i // 2, i % 2]
            ax.set_xlim(self.dt_columns[0], self.dt_columns[-1])
            ax.xaxis.set_major_locator(daily_major_locator)
            ax.xaxis.set_minor_locator(daily_minor_locator)
            ax.xaxis.set_major_formatter(date_formatter)
            ax.yaxis.grid()
            
        plt.legend()
        
        if savefig:
            plt.savefig(f'{self.datatype}.png')


    def __str__(self):
        return f"{color.BOLD}Data for COVID-19{color.END}\nType: {self.datatype.capitalize()}\nTime (UTC): {self.datetime_str}\n{color.BOLD}TOTAL: {self.total_cases}{color.END}"
    
    def __repr__(self):
        return self.__str__()

    
    
if __name__ == '__main__':
    confirmedData = Data('confirmed')
    print(confirmedData)
    confirmedData.plot(countries=('Portugal', 'Italy', 'Spain', 'US'), savefig=True)
    