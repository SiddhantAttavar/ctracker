from collections import defaultdict
from math import pow

def get_probability(a, b):
	return 1.0 / (1 + pow(10, (a - b) / 400.0))

def get_elo_ratings(problem_list):
	# Returns the elo rating of the user in list of problems
	rating = defaultdict(lambda: 1400)
	k = 30
	for problem in problem_list:
		for tag in problem['tags']:
			pa = get_probability(rating[tag], problem['difficulty_rating'])
			rating[tag] += k * (problem['is_solved'] - pa)
	return rating

def combine_ratings(ratings, weights):
	# Return the weighted average of the ratings of individual tags
	final_rating = 0
	total_weight = 0
	for tag, rating in ratings.items():
		final_rating += weights[tag] * rating
		total_weight += weights[tag]
	return final_rating / total_weight

def get_problem_list():
	pass

def rank_candidates(candidates, requirements):
	# Rank the candidates according to their qualifications and the user requirements
	candidates_ratings = {}
	problem_list = get_problem_list(requirements.items())
	for candidate in candidates:
		ratings = get_elo_ratings(problem_list)
		candidates_ratings[candidate['handle']] = combine_ratings(ratings, requirements.values())
	
	ranked_candidates = sorted(candidates_ratings.items(), key = lambda x: -x[1])
	return ranked_candidates
