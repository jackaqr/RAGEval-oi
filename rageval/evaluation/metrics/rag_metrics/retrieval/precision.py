from .utils import exist_match, exist_match_p


class Precision:
    name:str = "Precision"
    def __init__(self, threshold=0.5, topk = 5):
        self.threshold = threshold
        self.topk = topk

    def calculate_precision(self, retrieves, ground_truths, language=None) -> float:
        # retrieves = retrieves[:self.topk]
        # match_count = sum(
        #     exist_match_p(retrieve, ground_truths, language=language)
        #     for retrieve in retrieves
        # )
        match_count = sum(
            exist_match(ground_truth, retrieves, language=language)
            for ground_truth in ground_truths
        )
        return match_count / len(retrieves) if retrieves else 0

    def __call__(self, doc, ground_truth, results, language=None) -> float:
        retrieves = [r for r in doc["prediction"].get("references", [])]  # Retrieves from prediction
        ground_truths =doc['ground_truth'].get('references', [])
        return self.calculate_precision(retrieves, ground_truths, language=language)
