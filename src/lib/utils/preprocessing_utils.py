import pandas as pd


class Preprocessing:
    """
        class for Data preprocessing 
    """

    def __init__(self):
        pass


    def split_time_context(self, execution_date):
        """
            Split execution_date (datetime)
            into 
                ymd : YYYY-MM-DD 
                hm  : HHMM (HourMinute)
        """
        ymd = execution_date.strftime("%Y-%m-%d")
        hm = execution_date.strftime("%H%M")
        return ymd, hm


    def preprocessing_daily_library_loan(self, df, ymd):
        """
            Separate Genre (class_nm) and select only usefull columns
            param
                df : DataFrame (pandas)
        """

        # Column normalize
        df = df.rename(columns={
            'doc.bookname': 'bookname',
            'doc.isbn13': 'isbn13',
            'doc.loan_count': 'loan_count',
            'doc.class_nm': 'class_nm',
        })

        classes = ( 
            df['class_nm'].str.split(',').str[0].str.strip().str.split('>')
            .apply(lambda x: [c.strip() for c in x])
            .apply(lambda x: (x + [pd.NA, pd.NA, pd.NA])[:3])
        )

        df[['class1', 'class2', 'class3']] = pd.DataFrame(
            classes.tolist(),
            index=df.index
        )

        # Date
        df['date'] = ymd.replace('-', '')

        # Take only using columns 
        df = df[['date', 'bookname', 'isbn13', 'loan_count', 'class1', 'class2', 'class3']]

        return df



    def preprocessing_kma_daily_weather(self, df):
        """
            Extract only usefull columns
            convert -9 and -99 (imputed from kma) to set pd.NA
            Compute 체감온도 for winter and 불쾌지수 for summer
            param
                df : Pandas Data Frame of dataset
        """
        # preprocessing

        meaningful_columns = ['관측일', '평균기온', '최고기온', '최저기온', 
                            '강수량', '강수계속시간', '평균풍속', '최대풍속', 
                            '평균_전운량', '가조시간', '평균_상대습도']

        temp_cols = ['평균기온', '최고기온', '최저기온']
        other_cols = ['강수량', '강수계속시간', '평균풍속', '최대풍속', 
                            '평균_전운량', '가조시간', '평균_상대습도']

        df = df.loc[:, meaningful_columns]


        df[temp_cols] = (
            df[temp_cols]
            .replace(['-99', '-99.0', '-99.00', -99, -99.0, -99.00], pd.NA)
            .apply(pd.to_numeric, errors='coerce')
        )

        df[other_cols] = (
            df[other_cols]
            .replace(['-9', '-9.0', '-9.00', -9, -9.0, -9.00], pd.NA)
            .apply(pd.to_numeric, errors='coerce')
        )
                


        df['체감온도'] = pd.NA

        mask_winter = (df['평균기온'] <= 10) & (df['평균풍속'] >= 1.3)

        df.loc[mask_winter, '체감온도'] = (
            13.12
            + 0.6215 * df.loc[mask_winter, '평균기온']
            - 11.37 * (df.loc[mask_winter, '평균풍속'] ** 0.16)
            + 0.3965 * df.loc[mask_winter, '평균기온']
            * (df.loc[mask_winter, '평균풍속'] ** 0.16)
        )


        df['불쾌지수'] = pd.NA

        mask_summer = df['평균기온'] >= 24

        df.loc[mask_summer, '불쾌지수'] = (
            df.loc[mask_summer, '평균기온']
            + 0.36 * df.loc[mask_summer, '평균_상대습도']
            + 41.2
        )

        df['불쾌지수'] = df['불쾌지수'].clip(upper=85)

        return df
    


    def merge_dfs_on_date(self, df1, df2):
        """
            Merge two different data frame on date
                weather -> '관측일'
                library -> date
            param:
                df1 : Weather data
                df2 : Library data
        """
        
        df1 = df1.copy()
        df2 = df2.copy()

        df1['관측일'] = df1['관측일'].astype(str)
        df2['date'] = df2['date'].astype(str)

        merged = pd.merge(df2, df1, how='left', left_on='date', right_on='관측일')

        merged = merged.drop(columns=['관측일'])
        return merged