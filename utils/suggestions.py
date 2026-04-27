def suggest_questions(columns):

    columns = [c.lower() for c in columns]

    questions = []

    if "sales" in columns or "revenue" in columns:
        questions.append("Analyze Revenue Trend")

    if "customer_id" in columns or "customer" in columns:
        questions.append("Customer Segmentation")

    if "amount" in columns or "transaction" in columns:
        questions.append("Detect Anomalies")

    questions.append("Dataset Summary")

    return questions