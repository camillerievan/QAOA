import os
import sqlite3
import dbMsSql as sql
import networkx as nx
import networkx.algorithms.approximation.maxcut as classical_maxcut
import shutil
import ast # used to transform string to 'list of tuples'

# move Dante sqlite3 file to local Sql Server file QuantumMaxCut database

sourceDanteSqlFolder = 'C:\Bikini Atoll\QUANTUM\ex02'
ref_index = 'D_'
archiveDanteSqlFolder = sourceDanteSqlFolder + '/_archive'

# RUN THIS BEFORE ON THE SOURCE DB
'''
1. Add AR real field in tb_Test

2. run the following on SQLite

update tb_Test
UPDATE tb_Test
SET AR = (
    SELECT (SUM(cut.Cut * cut.Percentage / 100) / g.BruteForceMaxcut)
    FROM tb_Test_Cut cut
    INNER JOIN tb_Test tst ON tst.test_pk = cut.test_fk
    INNER JOIN tb_Graph g ON g.graph_pk = tst.graph_fk
    WHERE cut.test_fk = tb_Test.test_pk
    GROUP BY cut.test_fk
);

3. after running this function, run the following on MSSQL

update [dbo].[tb_Test]
set [n] = g.graph_nodes
from [dbo].[tb_Test] t
    inner join [dbo].[tb_Graph] g on g.graph_pk = t.graph_fk;

'''

# loop Dante sqlite3 folder for each db
# iterating over all files
for dbname in os.listdir(sourceDanteSqlFolder):
    if dbname.endswith('.db'):
        print(dbname)  # printing file name
        #print(dbname[7:22])

        # open Dante sqlite3
        conn = sqlite3.connect(f'{sourceDanteSqlFolder}/{dbname}')

        # tb_Graph
        cG = conn.cursor()
        cG.row_factory = sqlite3.Row
        cG.execute('SELECT * FROM tb_Graph') # LIMIT 10
        for rG in cG:
            gdante_fk = rG['graph_pk']
            graph_pk = sql.insert_db('tb_Graph', 'graph_pk'
                                    , ('DanteDb'   , 'Dante_fk' , '_date'    , 'graph_nodes', 'graph_edges','graph_is_weighted', 'graph_weight', 'graph_average_degree', 'graph_average_degree_connectivity', 'graph_density','graph_clustering', 'graph_average_clustering', 'graph_average_geodesic_distance','graph_betweenness_centrality', 'graph_average_betweenness_centrality', 'graph_max'    )
                                    ,     (dbname      , gdante_fk  , rG['_date'], rG['Nodes']  , rG['Edges']  , rG['IsWeighted']  , rG['Weight']  , rG['AverageDegree']   , rG['AverageDegreeConnectivity']    , rG['Density']  , rG['Clustering'] , rG['AverageClustering']   , rG['AverageGeodesicDistance']    ,rG['BetweennessCentrality']   , rG['AverageBetweennessCentrality']    , rG['BruteForceMaxcut'])
                                    )
            # tb_Test
            cT = conn.cursor()
            cT.row_factory = sqlite3.Row
            cT.execute(f'SELECT * FROM tb_Test WHERE graph_fk={gdante_fk}') # LIMIT 10
            for rT in cT:
                tdante_fk = rT['test_pk']
                test_pk = sql.insert_db('tb_Test', 'test_pk'
                                         , ('DanteDb', 'Dante_fk', '_date'    , 'execution_ref'               , 'n', 'graph_fk', 'maximize', 'layers', 'initial_angles_type'  , 'execution_time'   , 'nfev'    , 'expectation'    , 'classical_call_count', 'result'    , '[QAOA-CD]'      , 'AR')
                                         ,     (dbname   , tdante_fk , rT['_date'], ref_index + rT['ExecutionRef'], 0  , graph_pk  ,  1         , rT['p'] , rT['InitialAnglesType'], rT['ExecutionTime'], rT['nfev'], rT['Expectation'], rT['Iteration Count'] , rT['Maxcut'], rT['SecondOrder'], rT['AR'])
                                         )

                '''
                # tb_Test_Angle
                cAn = conn.cursor()
                cAn.row_factory = sqlite3.Row
                cAn.execute(f'SELECT * FROM tb_Test_Angle WHERE test_fk={tdante_fk}')
                for rAn in cAn:
                    sql.insert_db('tb_Test_Angle', 'testangle_pk'
                                  , ('Dante_fk'         , 'test_fk', 'minimize_iteration'     , 'expectation'     , 'angle_string'      )
                                  , (rAn['testangle_pk'], test_pk  , rAn['minimize_iteration'], rAn['expectation'], rAn['angle_string'])
                                  )
                cAn.close()
                '''

            cT.close()

        cG.close()
        conn.close()

        # move Dante sqlite3 to archive folder
        shutil.move(f'{sourceDanteSqlFolder}/{dbname}', f'{archiveDanteSqlFolder}/{dbname}')
