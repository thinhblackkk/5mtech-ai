class FiveMTechMemoryParser:

    def extract(self, question):

        question = question.strip()

        lower_question = question.lower()


        if lower_question.startswith("tao tên là "):

            name = question[11:].strip()

            if name:

                return {
                    "name": name
                }


        if lower_question.startswith("tao tên "):

            name = question[8:].strip()

            if name:

                return {
                    "name": name
                }


        if lower_question.startswith("tao làm "):

            job = question[8:].strip()

            if job:

                return {
                    "job": job
                }

        if lower_question.startswith("tao thích "):

            preference = question[10:].strip()

            if preference:

                return {
                    "preferences": [preference]
                }


        return {}