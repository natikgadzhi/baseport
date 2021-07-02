import basecampy3


class Comment(basecampy3.endpoints.recordings.Recording):
    def __str__(self):
        return f"Comment: {self._values.content}"


class Comments(basecampy3.endpoints.recordings.RecordingEndpoint):
    OBJECT_CLASS = Comment
    LIST_URL = "{base_url}/buckets/{project_id}/recordings/{parent_id}/comments.json"

    def list(self, project_id: int, parent_id: int) -> [Comment]:
        """
        Get the list of comments for a particular recording.
        :param project_id: a Project ID
        :type project_id: int
        :param parent_id: parent Record ID
        :type parent_id: int
        :return: a list of Comments for the Record
        :rtype: collections.Iterable[Comment]
        """
        url = self.LIST_URL.format(base_url=self.url, project_id=project_id, parent_id=parent_id)
        return self._get_list(url)


def _get_comments(self):
    """
    Fetch the list of comments for this Recording.
    """
    return Comments(self._endpoint._api).list(self.project_id, self.id)


basecampy3.endpoints.recordings.Recording.comments = _get_comments
