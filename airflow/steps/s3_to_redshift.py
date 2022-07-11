from psycopg2 import sql
import psycopg2
import sys

account_id = "916583527825"
redshift_cluster_hostname = "redshift-cluster-pipeline.conbfb3kvaou.sa-east-1.redshift.amazonaws.com"
redshift_password = "1231231Aa"
redshift_port = 5439
redshift_role = "RedShiftLoadRole"
redshift_username = "awsuser"
s3_bucket_name = "houses-data-bucket-1232742434897"
TABLE_NAME = 'houses'

file_path = f"s3://{s3_bucket_name}/raw/data"
role_string = f'arn:aws:iam::{account_id}:role/{redshift_role}'

sql_create_table = sql.SQL("""CREATE TABLE IF NOT EXISTS {table} (
                            Transacao varchar PRIMARY KEY,
                            Preco_da_transacao float,
                            Data timestamp,
                            Código_Postal varchar,
                            Tipo_de_propriedade varchar,
                            Construcao_nova varchar,
                            Tipo_de_ocupacao varchar,
                            Nome_do_edifício varchar(max),
                            Número varchar,
                            Rua varchar,
                            Coluna_10 varchar,
                            Cidade varchar,
                            Distrito varchar,
                            Coluna_14 varchar,
                            Coluna_15 varchar,
                            Código_Postal_do_edifício varchar
                            );""").format(table=sql.Identifier(TABLE_NAME))

create_temp_table = sql.SQL("CREATE TEMP TABLE our_staging_table (LIKE {table});").format(
    table=sql.Identifier(TABLE_NAME))

sql_copy_to_temp = (
    f"COPY our_staging_table FROM '{file_path}' iam_role '{role_string}' IGNOREHEADER 1 DELIMITER ',' CSV;"
)

delete_from_table = sql.SQL(
    "DELETE FROM {table} USING our_staging_table WHERE {table}.Transacao = our_staging_table.Transacao;").format(
    table=sql.Identifier(TABLE_NAME))

insert_into_table = sql.SQL("INSERT INTO {table} SELECT * FROM our_staging_table;").format(
    table=sql.Identifier(TABLE_NAME))

drop_temp_table = "DROP TABLE our_staging_table;"

def main():
    """Upload file form S3 to Redshift Table"""
    rs_conn = connect_to_redshift()
    load_data_into_redshift(rs_conn)

def connect_to_redshift():
    """Connect to Redshift instance"""
    try:
        rs_conn = psycopg2.connect(dbname='dev', user=redshift_username, password=redshift_password,
                                   host=redshift_cluster_hostname, port=redshift_port)
        return rs_conn
    except Exception as e:
        print(f"Unable to connect to Redshift. Error {e}")
        sys.exit(1)


def load_data_into_redshift(rs_conn):
    """Load data from S3 into Redshift"""
    with rs_conn:
        cur = rs_conn.cursor()
        cur.execute(sql_create_table)
        cur.execute(create_temp_table)
        cur.execute(sql_copy_to_temp)
        cur.execute(delete_from_table)
        cur.execute(insert_into_table)
        cur.execute(drop_temp_table)

        # Commit only at the end, so we won't end up
        # with a temp table and deleted main table if something fails
        rs_conn.commit()

if __name__ == '__main__':
    main()