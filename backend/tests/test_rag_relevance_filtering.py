from app.rag.retrieval import filter_relevant_documents


def test_filter_relevant_documents_rejects_wrong_job_family():
    docs = [
        {
            "doc_id": 1,
            "title": "FastAPI 技能定义",
            "doc_type": "backend",
            "score": 0.91,
            "metadata": {"job_family": "software_engineering"},
        },
        {
            "doc_id": 2,
            "title": "SQL 数据分析能力标准",
            "doc_type": "data_analysis",
            "score": 0.86,
            "metadata": {"job_family": "data_analysis"},
        },
    ]

    filtered = filter_relevant_documents(
        docs,
        job_family="data_analysis",
        allowed_doc_types=["data_analysis", "statistics"],
        min_score=0.75,
    )

    assert [doc["doc_id"] for doc in filtered] == [2]


def test_filter_relevant_documents_rejects_low_score():
    docs = [
        {
            "doc_id": 3,
            "title": "SQL 数据分析能力标准",
            "doc_type": "data_analysis",
            "score": 0.42,
            "metadata": {"job_family": "data_analysis"},
        }
    ]

    assert filter_relevant_documents(docs, "data_analysis", ["data_analysis"], 0.75) == []
