from django.shortcuts import render
import pandas as pd
from .analytics import ProcurementAnalytics
def home(request):
    return render(request, 'home.html')

def dashboard_page(request):
    if request.method == "POST":
        file = request.FILES["myFile"]
        pa = ProcurementAnalytics(file)
        total_sale = pa.total_sale
        profit = pa.profit
        return render(request, "dashboard_page.html",
                      {"something": True,
                       'total_sale': total_sale,
                       'profit': profit,
                       })
    else:
        return render(request, 'dashboard_page.html')