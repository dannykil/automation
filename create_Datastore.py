from google.cloud import discoveryengine_v1 as discoveryengine


def create_session(
    project_id: str,
    location: str,
    engine_id: str,
    user_pseudo_id: str,
) -> discoveryengine.Session:
    """Creates a session.

    Args:
        project_id: The ID of your Google Cloud project.
        location: The location of the app.
        engine_id: The ID of the app.
        user_pseudo_id: A unique identifier for tracking visitors. For example, this
          could be implemented with an HTTP cookie, which should be able to
          uniquely identify a visitor on a single device.
    Returns:
        discoveryengine.Session: The newly created Session.
    """

    client = discoveryengine.ConversationalSearchServiceClient()

    session = client.create_session(
        # The full resource name of the engine
        parent=f"projects/{project_id}/locations/{location}/collections/default_collection/engines/{engine_id}",
        session=discoveryengine.Session(user_pseudo_id=user_pseudo_id),
    )

    # Send Session name in `answer_query()`
    print(f"Session: {session.name}")
    return session

create_session("gen-lang-client-0480088393", "global", "tutorial-web-app_1734764513627", "jm.kil@demo.gws.hist.co.kr")

# 1) 로그인
# * gcloud auth list
# gcloud auth login jm.kil@demo.gws.hist.co.kr
# gcloud auth application-default login --impersonate-service-account jm.kil@demo.gws.hist.co.kr
# 2) 프로젝트 설정
# gcloud config set project gen-lang-client-0480088393