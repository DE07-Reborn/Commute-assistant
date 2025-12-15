import requests
import os
import logging

class Library_api_collector:
    """
        Request api from library to collect loan book information
    """

    def __init__(self, ymd):
        """
            Initialize Class 
            param
                ymd : Year-Month-Day
        """
        self.ymd = ymd

        self.key = os.getenv("LIBRARY_KEY")
        if not self.key:
            raise EnvironmentError("LIBRARY_KEY is not set in environment variables")

        # Default timeout 
        self.base_timeout = 10



    def request_loan_data(self):
        """
            Collecting Book Loan data via API Request
            Here, the default setting explained on parameter below
            Mainly, Request the loan data daily using Airflow dag
        """
        library_url = 'https://data4library.kr/api/loanItemSrch'

        """
            Parameters
            authKey : API Access key
            startDt : Start date of loan data
            endDt : end date of loan data -> set for 1 day
            from_age : Minimum age of book shows
            addCode : code for books' genre
            pageSize : The amount of data provided by reqeusts
            format : json (for default its XML)
        """
        library_params = {
            'authKey' : self.key,
            'startDt' : self.ymd,
            'endDt' : self.ymd,
            'from_age' : 16,
            'addCode': '0;1;2;4;9',
            'pageSize' : 3000,
            'format' : 'json'
        }

        # Requests API 
        logging.info("Library API request started")
        try:
            response = requests.get(library_url, params=library_params, 
                                    timeout=self.base_timeout)
            
            # Check api status
            response.raise_for_status()

            data = response.json()

            docs = data.get("response", {}).get("docs", [])
            
            if not docs:
                logging.error("Library API returned empty docs")
                raise ValueError("Library API returned empty docs")

            logging.info('Request API success')

            # return json file
            return data

        except requests.Timeout:
            logging.error('Library API request timeout')
            raise

        except requests.HTTPError as exc:
            logging.error(f"Library API HTTP error: {exc}")
            raise

        except Exception:
            logging.exception("Unexpected error while requesting Library API")
            raise
