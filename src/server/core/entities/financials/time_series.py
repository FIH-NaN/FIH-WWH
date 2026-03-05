
import numpy as np
import pandas as pd

from src.server.core.entities.financials.object import FinancialObject


class TimeSeriesData:
    
    obj: FinancialObject
    data: pd.DataFrame

    
