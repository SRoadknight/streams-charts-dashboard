from streamlit.connections import BaseConnection
from streamlit.runtime.caching import cache_data

import duckdb
import pandas as pd

class MotherDuckConnection(BaseConnection[duckdb.DuckDBPyConnection]):
    """Basic st.base_connection implementation for DuckDB/MotherDuck"""

    def _connect(self, **kwargs) -> duckdb.DuckDBPyConnection:
        if 'database' in kwargs:
            db = kwargs.pop('database')
        else:
            db = self._secrets['database']
        return duckdb.connect(database=db, **kwargs)
    
    def cursor(self) -> duckdb.DuckDBPyConnection:
        return self._instance.cursor()

    def query(self, query: str, ttl: int = 3600, params: object = None, index_col=None, **kwargs) -> pd.DataFrame:
        @cache_data(ttl=ttl)
        def _query(query: str, params: tuple = None, **kwargs) -> pd.DataFrame:
            cursor = self.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.df()
        
        df =  _query(query, params=params, **kwargs)
        if index_col:
            df.set_index(index_col, inplace=True)
        return df
