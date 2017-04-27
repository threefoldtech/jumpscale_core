from path import Path


class PathFactory:

    def get(self, startpath):
        """
        example1:
        ```
        d = j.tools.path.get("/tmp")
        for i in d.walk():
            if i.isfile():
                if i.name.startswith("something_"):
                    i.remove()
        ```

        other:
        files = d.walkfiles("*.pyc")
        num_files = len(d.files())
        """
        return Path(startpath)