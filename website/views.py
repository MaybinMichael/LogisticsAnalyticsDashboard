from django.shortcuts import render
import pandas as pd
from .analytics import ProcurementAnalytics
def home(request):
    return render(request, 'home.html')

def dashboard_page(request):
    if request.method == "POST":
        file = request.FILES["myFile"]
        pa = ProcurementAnalytics(file)
        return render(request, "dashboard_page.html",
                      {"something": True,
                       'total_sale': pa.total_sale,
                       'profit': pa.profit,
                       'fig_plot_sales_month_year_wise': pa.fig_plot_sales_month_year_wise,
                       'fig_plot_sale_month_wise' : pa.fig_plot_sale_month_wise,
                       'fig_plot_sales_country_wise' : pa.fig_plot_sales_country_wise,
                       'fig_plot_product_units_discount' : pa.fig_plot_product_units_discount,
                       'fig_plot_product_sales' : pa.fig_plot_product_sales,
                       })
    else:
        return render(request, 'dashboard_page.html')