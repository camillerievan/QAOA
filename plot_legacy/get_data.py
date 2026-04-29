import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from local_library import GraphResultType, GraphType, InitialAngle, AngleType, ClassicalAlgorithm


def get_dataset(ia:InitialAngle=InitialAngle.All
              , graphType:GraphType=GraphType.All
              , testIndex:str=None
              , layers:int=None
              , angle_study:AngleType=None
              , graph_result_type:GraphResultType=None
              , classical_algo:ClassicalAlgorithm=ClassicalAlgorithm.All
              , isQAOACD: bool = False  ):
    """
    Connects to the SQL Server and calls the appropriate stored procedure based on testIndex.
    Returns the result as a pandas DataFrame.

    Parameters:
        graphType (GraphType, optional): Required if testIndex is 'A', 'B', or 'AB'.
        testIndex (str): Determines which stored procedure to call. Expected values: 'A', 'B', 'AB', 'C', 'D'.
        layers (int, optional): Required if testIndex is 'A', 'B', or 'AB'.
        angle_study (str): Required for both stored procedures.
        graph_result_type (GraphResultType): Required for both stored procedures.

    Returns:
        pandas.DataFrame: The dataset returned by the stored procedure, including headers.

    Raises:
        ValueError: If required parameters are missing or testIndex is invalid.
        Exception: If there's an issue with the database operation.
    """

    # Define your connection string
    server = 'localhost'
    database = 'Quantum_MaxCut_20250210' #'Quantum_MaxCut_20240808'
    if testIndex == 'COMPARE1-2':
        database = 'Quantum_MaxCut_20250210'
    username = 'sa'
    password = 'nexus123'
    driver = 'ODBC Driver 17 for SQL Server'

    connection_string = (
        f'mssql+pyodbc://{username}:{quote_plus(password)}@{server}/{database}'
        f'?driver={quote_plus(driver)}'
    )

    try:
        # Create SQLAlchemy engine
        engine = create_engine(connection_string)

        # Determine which stored procedure to call
        if testIndex in ['A', 'B', 'AB']:
            if graphType is None or layers is None or angle_study is None or graph_result_type is None:
                raise ValueError("Missing parameters for chart_helper_thesis_AB")

            # Prepare the EXEC statement for chart_helper_thesis_AB
            exec_query = f"EXEC [dbo].[chart_helper_thesis_AB] @initial_angles={ia.value}, @graphType={graphType.value}, @testIndex='{testIndex}', @layers={layers}, @angle_study='{angle_study.value}', @type={graph_result_type.value}, @classical_algorithm={classical_algo.value}"

        elif testIndex in ['C', 'D']:
            if angle_study is None or graph_result_type is None:
                raise ValueError("Missing parameters for chart_helper_thesis_CD")

            # Prepare the EXEC statement for chart_helper_thesis_CD
            exec_query = f"EXEC [dbo].[chart_helper_thesis_CD] @initial_angles={ia.value}, @testIndex='{testIndex}', @angle_study='{angle_study.value}', @type={graph_result_type.value}, @classical_algorithm={classical_algo.value}"

        elif testIndex == '':
            if angle_study is None or graph_result_type is None:
                raise ValueError("Missing parameters for chart_helper_thesis_ALL")

            # Prepare the EXEC statement for chart_helper_thesis_ANGLE
            exec_query = f"EXEC [dbo].[chart_helper_thesis_ALL] @initial_angles={ia.value}, @angle_study='{angle_study.value}', @type={graph_result_type.value}"

        elif testIndex == 'COMPARE1-2':
            exec_query = f"EXEC [dbo].[chart_helper_thesis_QAOACD] @layers={layers}, @qaoacd={1 if isQAOACD else 0}, @type={graph_result_type.value}"

        else:
            raise ValueError("Invalid testIndex value. Expected 'A', 'B', 'AB', 'C', or 'D'.")

        # Use pandas to execute the query and fetch the data as a DataFrame
        with engine.connect() as connection:
            df = pd.read_sql(exec_query, connection)

        return df

    except Exception as e:
        # Handle database errors
        print("An error occurred:", e)
        raise
