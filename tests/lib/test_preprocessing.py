import pytest
from datetime import datetime
import pandas as pd

from src.lib.utils.preprocessing_utils import Preprocessing

##############################
#       Fixture
##############################
@pytest.fixture
def library_df():
    return pd.DataFrame({
        'doc.bookname': ['나를 키우는 시'],
        'doc.isbn13': ['9791189228576'],
        'doc.loan_count': ['1'],
        'doc.class_nm': ['문학 > 한국문학 > 시'],
    })

@pytest.fixture
def ymd():
    return '2025-12-15'


@pytest.fixture
def kma_sample_df():
    return pd.DataFrame([{
        '관측일': '20251211',
        '평균기온': '5',
        '최고기온': '8',
        '최저기온': '-1',
        '강수량': '0',
        '강수계속시간': '0',
        '평균풍속': '2.0',   
        '최대풍속': '5.0',
        '평균_전운량': '5',
        '가조시간': '8.0',
        '평균_상대습도': '60'
    }])




# Test split_time_context
def test_split_time_context_basic():
    preprocessing = Preprocessing()
    execution_date = datetime(2025, 12, 12, 23, 50)

    ymd, hm = preprocessing.split_time_context(execution_date)

    assert ymd == '2025-12-12'
    assert hm == '2350'


# Test preprocessing daily library loan data frame
def test_preprocessing_daily_library_loan_success(library_df, ymd):
    preprocesor = Preprocessing()

    result = preprocesor.preprocessing_daily_library_loan(library_df, ymd)

    # Check pandas df out
    assert isinstance(result, pd.DataFrame)

    # Check columlns
    assert list(result.columns) == [
        'date',
        'bookname',
        'isbn13',
        'loan_count',
        'class1',
        'class2',
        'class3',
    ]

    # Chcek Values
    assert result.loc[0, 'date'] == '20251215'
    assert result.loc[0, 'bookname'] == '나를 키우는 시'
    assert result.loc[0, 'isbn13'] == '9791189228576'
    assert result.loc[0, 'loan_count'] == '1'
    assert result.loc[0, 'class1'] == '문학'
    assert result.loc[0, 'class2'] == '한국문학'
    assert result.loc[0, 'class3'] == '시'



# Test genre has only two parts
def test_preprocessing_daily_library_loan_two_genre(library_df, ymd):
    library_df['doc.class_nm'] = '문학 > 한국문학'

    preprocessor = Preprocessing()
    result = preprocessor.preprocessing_daily_library_loan(library_df, ymd)

    # Valificate Genre
    assert result.loc[0, 'class1'] == '문학'
    assert result.loc[0, 'class2'] == '한국문학'
    assert pd.isna(result.loc[0, 'class3'])
    

# Test multiple items
def test_preprocessing_daily_library_loan_multiple_items(ymd):
    df = pd.DataFrame({
        'doc.bookname': ['책1', '책2'],
        'doc.isbn13': ['111', '222'],
        'doc.loan_count': ['1', '2'],
        'doc.class_nm': [
            '문학 > 한국문학 > 시',
            '문학 > 외국문학 > 소설'
        ],
    })

    preprocessor = Preprocessing()
    result = preprocessor.preprocessing_daily_library_loan(df, ymd)

    assert len(result) == 2
    assert result.iloc[1]['class3'] == '소설'

    
# Test Preprocessing for kma weather dataset
# Success case
def test_preprocessing_kma_daily_weather_success(kma_sample_df):
    preprocessor = Preprocessing()
    result = preprocessor.preprocessing_kma_daily_weather(kma_sample_df)

    # check reulst is pd.dataFrame
    assert isinstance(result, pd.DataFrame)

    # Check 체감온도 and 불쾌지수
    assert pd.notna(result.loc[0, '체감온도'])
    assert pd.isna(result.loc[0, '불쾌지수'])

# Test 불쾌지수
def test_preprocessing_kma_daily_weather_discomfort_index():
    df = pd.DataFrame([{
        '관측일': '20250720',
        '평균기온': '32',
        '최고기온': '36',
        '최저기온': '27',
        '강수량': '5',
        '강수계속시간': '2',
        '평균풍속': '1.0',
        '최대풍속': '3.0',
        '평균_전운량': '7',
        '가조시간': '6.0',
        '평균_상대습도': '80'
    }])

    preprocessor = Preprocessing()
    result = preprocessor.preprocessing_kma_daily_weather(df)

    assert pd.notna(result.loc[0, '불쾌지수'])
    assert result.loc[0, '불쾌지수'] <= 85


# Test imputation
def test_preprocessing_kma_daily_weather_imputation():
    df = pd.DataFrame([{
        '관측일': '20250101',
        '평균기온': '-99',
        '최고기온': '-99.0',
        '최저기온': '-99',
        '강수량': '-9',
        '강수계속시간': '-9',
        '평균풍속': '-9',
        '최대풍속': '-9',
        '평균_전운량': '-9',
        '가조시간': '-9',
        '평균_상대습도': '-9'
    }])

    preprocessor = Preprocessing()
    result = preprocessor.preprocessing_kma_daily_weather(df)

    assert result['평균기온'].isna().all()
    assert result['강수량'].isna().all()
    assert pd.isna(result.loc[0, '체감온도'])
    assert pd.isna(result.loc[0, '불쾌지수'])


# Test merge method
# success
def test_merge_dfs_on_date_success():
    weather_df = pd.DataFrame([
        {'관측일': '20251214', '평균기온': 5, '체감온도': 2}
    ])

    library_df = pd.DataFrame([
        {'date': '20251214', 'bookname': '책'}
    ])

    preprocessor = Preprocessing()
    result = preprocessor.merge_dfs_on_date(weather_df, library_df)

    assert len(result) == 1
    assert result.loc[0, '평균기온'] == 5
    assert result.loc[0, 'bookname'] == '책'


# Date diff
def test_merge_dfs_on_date_diff():
    weather_df = pd.DataFrame([
        {'관측일': '20251214', '평균기온': 5}
    ])

    library_df = pd.DataFrame([
        {'date': '20251213', 'bookname': '책'}
    ])

    preprocessor = Preprocessing()
    result = preprocessor.merge_dfs_on_date(weather_df, library_df)

    assert len(result) == 1
    assert result.loc[0, 'bookname'] == '책'
    assert pd.isna(result.loc[0, '평균기온'])

# Multiple rows of library
def test_merge_dfs_on_date_multiple():
    weather_df = pd.DataFrame([
        {'관측일': '20251214', '평균기온': 3}
    ])

    library_df = pd.DataFrame([
        {'date': '20251214', 'bookname': '책1'},
        {'date': '20251214', 'bookname': '책2'}
    ])

    preprocessor = Preprocessing()
    result = preprocessor.merge_dfs_on_date(weather_df, library_df)

    assert len(result) == 2
    assert result['평균기온'].tolist() == [3, 3]