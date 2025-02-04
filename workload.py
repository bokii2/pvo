from flask import Flask, request, jsonify 
import time

app = Flask(__name__)

@app.route('/sum') 
def sum primes():
	try: 
		n = int (request.args.get('n', 10)) 
		start_time = time.time() 
		def is prime (num): 
			if num < 2: 
				return False 
			for i in range(2, int (num ** 0.5) + 1): 
				if num%i==0: 
					return False 
			return True

		prime_sum = sum(num for num in range (2, n + 1) if is_prime (num))

		end time = time.time() 
		return jsonify({'n': n, 'sum_of_primes': prime_sum, 'time': end_time start_time}) 
	except ValueError:
		return jsonify({'error': 'Invalid input'}), 700 

if __name__ == "__main__": 
	app.run(host="0.0.0.0", port=5000)
