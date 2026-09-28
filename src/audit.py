from sqlalchemy import text

def start_pipeline_run(
        connection,
        ingestion_id,
        pipeline_name,
        source_system        
):
    t = text("""
    INSERT INTO audit.PipelineRun
    (
        ingestion_id,
        pipeline_name,
        source_system,
        start_time,
        status
    )
    VALUES
    (
        :ingestion_id,
        :pipeline_name,
        :source_system,
        SYSUTCDATETIME(),
        :status
    )
     """)


    connection.execute(t,
    {
        "ingestion_id": ingestion_id,
        "pipeline_name": pipeline_name,
        "source_system": source_system,
        "status": "STARTED"
    })


def complete_pipeline_run(
         connection,
         ingestion_id,
         events_count,
         devices_count,
         patients_count,
         mdr_text_count,
         ):
       

       t=text("""UPDATE audit.PipelineRun set 
                events_count=:events_count,
                devices_count=:devices_count,
                patients_count=:patients_count,
                mdr_text_count=:mdr_text_count,
                status='SUCCESS',
                end_time=SYSUTCDATETIME()
            where ingestion_id= :ingestion_id """)
       connection.execute(t,
        {
        "events_count":events_count,
        "devices_count":devices_count,
        "patients_count" :patients_count,
        "mdr_text_count": mdr_text_count,
        "ingestion_id" :ingestion_id                     
        }
                          )

def fail_pipeline_run(
            connection,
            ingestion_id,
            error_message):
      
      t=text("""UPDATE audit.PipelineRun
                SET error_message=:error_message,
                    end_time = SYSUTCDATETIME(),
                    status='Failed'
                   WHERE ingestion_id=:ingestion_id""")
      connection.execute(t,
                        {"error_message":error_message,
                         "ingestion_id":ingestion_id                     
                         }
                         )