from dotenv import load_dotenv
from snowflake.snowpark.session import Session
import os
from snowflake.core import Root
from typing import List
from snowflake.cortex import complete
from trulens.apps.custom import instrument
from trulens.providers.cortex.provider import Cortex
from trulens.core import Feedback
from trulens.core import Select
import numpy as np
from trulens.apps.custom import TruCustomApp
from trulens.core import TruSession
from trulens.connectors.snowflake import SnowflakeConnector
from trulens.dashboard import run_dashboard

load_dotenv()


connection_params = {
    "account":  os.getenv("SNOWFLAKE_ACCOUNT"),
    "user": os.getenv("SNOWFLAKE_USER"),
    "password": os.getenv("SNOWFLAKE_USER_PASSWORD"),
    "role": os.getenv("SNOWFLAKE_ROLE"),
    "database": os.getenv("SNOWFLAKE_DATABASE"),
    "schema": os.getenv("SNOWFLAKE_SCHEMA"),
    "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE")
}

snowpark_session = Session.builder.configs(connection_params).getOrCreate()
tru_snowflake_connector = SnowflakeConnector(account=os.getenv("SNOWFLAKE_ACCOUNT"),
                      user=os.getenv("SNOWFLAKE_USER"),
                      password= os.getenv("SNOWFLAKE_USER_PASSWORD"),
                      role = os.getenv("SNOWFLAKE_ROLE"),
                                             database=os.getenv("SNOWFLAKE_DATABASE"),
                                             schema=os.getenv("SNOWFLAKE_SCHEMA"),
                                             warehouse= os.getenv("SNOWFLAKE_WAREHOUSE"))

tru_session = TruSession(connector=tru_snowflake_connector)
tru_session.get_leaderboard()

run_dashboard(session=tru_session)


