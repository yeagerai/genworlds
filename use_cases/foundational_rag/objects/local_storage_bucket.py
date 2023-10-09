import os
from genworlds.objects.abstracts.object import AbstractObject
from genworlds.events.abstracts.action import AbstractAction
from genworlds.events.abstracts.event import AbstractEvent

import PyPDF2
from docx import Document as DocxDocument


# Define the Local Storage Bucket Object
class LocalStorageBucket(AbstractObject):
    def __init__(self, id:str, storage_path: str = "./"):
        self.storage_path = storage_path
        actions = [ConvertFolderToTxt(host_object=self)]

        super().__init__(name="LocalStorage Bucket", 
                         id=id, 
                         description="Object used to consolidate various document types into a single .txt file and store it locally.", 
                         actions=actions
                         )


# Event for agent's request to convert all files in a folder
class AgentRequestsFolderConversion(AbstractEvent):
    event_type = "agent_requests_folder_conversion"
    description = "An agent requests conversion of all supported documents in a specific folder to a single txt file."
    input_folder_path: str
    output_file_path: str


# Event sent by LocalStorageBucket to notify agent of completion
class FolderConversionCompleted(AbstractEvent):
    event_type = "folder_conversion_completed"
    description = "Notifies the agent that the folder has been successfully converted into a txt file."
    output_txt_path: str

class ConvertFolderToTxt(AbstractAction):
    trigger_event_class = AgentRequestsFolderConversion
    description = "Converts all supported documents in a specific folder to a single txt file."
    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)
    
    def __call__(self, event: AgentRequestsFolderConversion):
        all_texts = []
        input_folder_path = event.input_folder_path
        output_file_path = event.output_file_path

        for filename in os.listdir(input_folder_path):
            file_path = os.path.join(input_folder_path, filename)
            file_extension = os.path.splitext(filename)[1]

            if file_extension == ".md":
                with open(file_path, "r", encoding="utf-8") as f:
                    all_texts.append(f.read())

            elif file_extension == ".docx":
                doc = DocxDocument(file_path)
                doc_text = "\n".join([p.text for p in doc.paragraphs])
                all_texts.append(doc_text)

            elif file_extension == ".pdf":
                with open(file_path, "rb") as f:
                    reader = PyPDF2.PdfFileReader(f)
                    pdf_text = "\n".join(
                        [
                            reader.getPage(i).extractText()
                            for i in range(reader.numPages)
                        ]
                    )
                    all_texts.append(pdf_text)

        # Save consolidated text to a new txt file
        output_txt_path = os.path.join(self.host_object.storage_path, output_file_path)
        with open(output_txt_path, "w", encoding="utf-8") as f:
            f.write("\n\n---\n\n".join(all_texts))
        
        event = FolderConversionCompleted(
            sender_id=self.host_object.id,
            target_id=event.sender_id,
            output_txt_path=output_txt_path
        )
        self.host_object.send_event(event)