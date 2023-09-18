import pandas as pd
import numpy as np
import plotly.figure_factory as ff
import plotly.express as px
import plotly.graph_objects as go
import logging
import os

logging.basicConfig(filename="website/logs/log_file",
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
module_logger = logging.getLogger(__name__)

class ProcurementAnalytics():
    '''
    This class is to perform analytics computations
    '''
    _class_logger = module_logger.getChild(__qualname__)
    try:
        def __init__(self,file):
            self._instance_logger = self._class_logger.getChild(str(id(self)))
            flag = self.read_document(file)
            if flag:
                self.cont_var=[]
                self.clean_folder()
                self.preprocessing()
                self.summation()
                self.plot_sales_month_year_wise()
                self.plot_sale_month_wise()
                self.plot_sale_country_wise()
                self.plot_product_units_discount()
                self.describe_data()
                self.plot_product_sales()
            else:
                self.total_sale = 0
                self.profit = 0

        def preprocessing(self):
            # cleaning currency columns
            df_subset = self.df.copy()
            if self.document_type=='csv':
                currency_columns = ["Manufacturing Price", "Sale Price", "Gross Sales", "Discounts", "Sales", "COGS", "Profit"]
                for col in currency_columns:
                    df_subset1 = df_subset[col].str.replace("$", '').str.replace(",", '').str.replace("-",'0').str.replace(
                        " ", '').str.replace(")", '').str.replace("(", '-').to_frame().astype(float)
                    df_subset.drop(col, axis=1, inplace=True)
                    df_subset = pd.concat([df_subset, df_subset1], axis=1, join='inner')

            # cleaning categorical columns
            df_subset1 = df_subset['Month'].str.replace(" ", '').to_frame().astype(str)
            df_subset.drop('Month', axis=1, inplace=True)
            df_subset = pd.concat([df_subset, df_subset1], axis=1, join='inner')
            self.df = df_subset


        def show_distribution(self, feature=[]):
            hist_data = [self.df[feature]]
            group_labels = [feature]
            fig = ff.create_distplot(hist_data, group_labels)
            return fig
        def plot_sales_month_year_wise(self):
            df_subset = self.df[["Year", "Month", "Gross Sales"]]
            df_subset = pd.pivot_table(df_subset, values ='Gross Sales', index =['Year', 'Month'],
                             aggfunc = np.sum)
            df_subset = df_subset.reset_index().rename_axis(None, axis=1)

            months = ["January", "February", "March", "April", "May", "June",
                      "July", "August", "September", "October", "November", "December"]
            df_subset = df_subset.sort_values('Month', key=lambda x: pd.Categorical(x, categories=months, ordered=True))

            fig = px.line(df_subset, x="Month", y="Gross Sales", color='Year', markers=True)
            fig.update_layout(
                paper_bgcolor='#f1f1f1',
            )

            fig.write_image("website/plots_store/plot_gross_sales_month_year_wise.jpg")

        def summation(self):
            df_subset = self.df[self.df["Year"] == 2014]
            self.total_sale = round(df_subset["Sales"].sum()/1000000, 2)
            self.profit = round(df_subset["Profit"].sum()/1000000, 2)

        def plot_sale_month_wise(self):
            df_subset = self.df[self.df["Year"] == 2014]
            # get subset of data with Year, Month, Gross Sales
            df_subset = df_subset[["Month", "Sales"]]
            df_subset = pd.pivot_table(df_subset, values='Sales', index=['Month'],
                                       aggfunc=np.sum)
            df_subset = df_subset.reset_index().rename_axis(None, axis=1)

            months = ["January", "February", "March", "April", "May", "June",
                      "July", "August", "September", "October", "November", "December"]
            df_subset = df_subset.sort_values('Month', key=lambda x: pd.Categorical(x, categories=months, ordered=True))
            fig = px.line(df_subset, x="Month", y="Sales", width=600, height=200)
            fig.update_xaxes(title=None)
            fig.update_yaxes(title=None)
            fig.update_traces(line_color='green')
            fig.update_layout(
                paper_bgcolor='#f1f1f1',
            )

            fig.write_image("website/plots_store/plot_sales_month_wise.jpg")

        def plot_sale_country_wise(self):
            df_subset = self.df[self.df["Year"] == 2014]
            # get subset of data with Year, Month, Gross Sales
            df_subset = df_subset[["Country", "Sales"]]
            df_subset = pd.pivot_table(df_subset, values='Sales', index=['Country'],
                                       aggfunc=np.sum)
            df_subset = df_subset.reset_index().rename_axis(None, axis=1)

            # ISO Alpha naming for countries
            df_subset['iso_alpha'] = df_subset['Country']
            df_subset1 = df_subset['iso_alpha'].str.replace("Canada", 'CAN').str.replace("France", 'FRA').str.replace(
                "Germany", 'DEU').str.replace(
                "Mexico", 'MEX').str.replace("United States of America", 'USA').to_frame()
            df_subset.drop("iso_alpha", axis=1, inplace=True)
            df_subset = pd.concat([df_subset, df_subset1], axis=1, join='inner')

            fig = px.scatter_geo(df_subset, locations="iso_alpha", color="Country",
                                 hover_name="Country", size="Sales",
                                 )
            fig.update_layout(height=300, margin={"r": 0, "t": 0, "l": 0, "b": 0})
            fig.update_geos(
                landcolor='darkturquoise',
                oceancolor="LightBlue",
            )
            fig.update_layout(
                paper_bgcolor='#f1f1f1',
            )

            fig.write_image("website/plots_store/plot_sales_country_wise.jpg")

        def plot_product_units_discount(self):
            df_subset = self.df[self.df["Year"] == 2014]
            # get subset of data with Year, Month, Gross Sales
            df_subset = df_subset[["Product", "Units Sold", "Discounts"]]
            df_subset = pd.pivot_table(df_subset, values=['Units Sold', 'Discounts'], index=['Product'],
                                       aggfunc=np.sum)
            df_subset = df_subset.reset_index().rename_axis(None, axis=1)
            product = df_subset["Product"].values
            units = df_subset["Units Sold"].values
            discounts = df_subset["Discounts"].values

            fig = go.Figure(
                data=go.Bar(
                    x=product,
                    y=units,
                    name="Total units sold",
                    marker=dict(color="paleturquoise"),
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=product,
                    y=discounts,
                    yaxis="y2",
                    name="Total discounts given",
                    marker=dict(color="crimson"),
                )
            )

            fig.update_layout(
                legend=dict(orientation="h"),
                yaxis=dict(
                    title=dict(text="Total units sold"),
                    side="left",
                    range=[0,300000],
                ),
                yaxis2=dict(
                    title=dict(text="Total discounts given"),
                    side="right",
                    range=[0,2500000],
                    overlaying="y",
                    tickmode="sync",
                ),
            )
            fig.update_layout(
                paper_bgcolor='#f1f1f1',
            )

            fig.write_image("website/plots_store/plot_product_units_discount.jpg")

        def read_document(self, document_path):
            if '.csv' in str(document_path):
                self.document_type = 'csv'
                self.df = pd.read_csv(document_path)
                return True
            elif '.xlsx' in str(document_path) or '.xls' in str(document_path):
                self.document_type='excel'
                self.df = pd.read_excel(document_path)
                return True
            else:
                self._instance_logger.error("User uploaded file with formats other than .xlsx, .xls or .csv")
                return False

        def clean_folder(self):
            dir = 'website/plots_store'
            for f in os.listdir(dir):
                os.remove(os.path.join(dir, f))

        def describe_data(self):
            # Summary of continuous type data
            df_subset = self.df[self.df["Year"] == 2014]
            self.cont_var = ["Units Sold", "Manufacturing Price", "Sale Price", "Gross Sales", "Discounts", "Sales", "COGS", "Profit"]
            cont_data_summary = pd.DataFrame(data=None, index=self.cont_var)
            cont_data_summary = cont_data_summary.assign(Mean=round(df_subset[self.cont_var].mean(),2))
            cont_data_summary = cont_data_summary.assign(Standard_Deviation=round(df_subset[self.cont_var].std(),2))
            cont_data_summary = cont_data_summary.assign(Variance=round(df_subset[self.cont_var].var(),2))
            cont_data_summary = cont_data_summary.assign(Min=df_subset[self.cont_var].min())
            cont_data_summary = cont_data_summary.assign(Max=df_subset[self.cont_var].max())
            cont_data_summary = cont_data_summary.assign(First_Quartile=df_subset[self.cont_var].quantile(0.25))
            cont_data_summary = cont_data_summary.assign(Median=df_subset[self.cont_var].median())
            cont_data_summary = cont_data_summary.assign(Third_Quartile=df_subset[self.cont_var].quantile(0.75))
            cont_data_summary.reset_index(inplace=True)

            fig = go.Figure(data=[
                go.Table(
                    #columnorder=[1, 2,3,4,5,6,7,8],
                    #columnwidth=[10, 10, 10, 10, 10, 10, 10, 10],
                    header=dict(values=list(cont_data_summary.columns), align='center'),
                    cells=dict(values=cont_data_summary.values.transpose(),
                               fill_color=[["white", "lightgrey"] * cont_data_summary.shape[0]],
                               align='center',
                               height=30
                               )
                )
            ])
            fig.update_layout(width=1000,
                              height=300,
                              margin_b=0,
                              margin_l=0,
                              margin_r=0,
                              margin_t=0,
                              paper_bgcolor='#f1f1f1',
                              )
            fig.write_image("website/plots_store/plot_descriptive_statistics.jpg", scale=5)


        def plot_product_sales(self):
            df_subset = self.df[self.df["Year"] == 2014]
            # get subset of data with Year, Month, Gross Sales
            df_subset = df_subset[["Product", "Sales","Country"]]
            df_subset = pd.pivot_table(df_subset, values=['Sales'], index=['Product',"Country"],
                                       aggfunc=np.sum)
            df_subset = df_subset.reset_index().rename_axis(None, axis=1)

            fig = px.bar(df_subset, x="Sales", y="Product", color='Country', orientation='h',
                         hover_data=["Sales", "Country"],
                         height=400,
                         )
            fig.update_layout(margin_b=0,
                              margin_l=0,
                              margin_r=0,
                              margin_t=0,
                              paper_bgcolor='#f1f1f1',
                              )

            fig.write_image("website/plots_store/plot_product_sales.jpg")


    except Exception as e:
        _class_logger.error(e)






