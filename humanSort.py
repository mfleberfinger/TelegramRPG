# Sorts a list of arbitrary items based on user input.

# Function to find the partition position
def partition(array, low, high):

	# choose the rightmost element as pivot
	pivot = array[high]

	# pointer for greater element
	i = low - 1

	# traverse through all elements
	# compare each element with pivot
	for j in range(low, high):
		raw = "blank"
		while raw != "<" and raw != ">" and raw != "=":
			raw = input("{0} ? {1}\n".format(array[j], pivot))
		lessOrEqual = raw != ">"
		#if array[j] <= pivot:
		if lessOrEqual:
			# If element smaller than pivot is found
			# swap it with the greater element pointed by i
			i = i + 1
			# Swapping element at i with element at j
			(array[i], array[j]) = (array[j], array[i])
	# Swap the pivot element with the greater element specified by i
	(array[i + 1], array[high]) = (array[high], array[i + 1])
	# Return the position from where partition is done
	return i + 1
 
# function to perform quicksort
def quickSort(array, low, high):
	if low < high:

		# Find pivot element such that
		# element smaller than pivot are on the left
		# element greater than pivot are on the right
		pi = partition(array, low, high)

		# Recursive call on the left of pivot
		quickSort(array, low, pi - 1)

		# Recursive call on the right of pivot
		quickSort(array, pi + 1, high)


#data = [1, 2, 4, 0, 5, 10, -1, 5, 3, 3]
#print("data = {0}".format(data))


#quickSort(data, 0, len(data) - 1)


#print("data = {0}".format(data))


with open(input("Filename: "), "r") as f:
	arr = f.read().strip().split("\n")
	print("to sort:\n{0}".format(arr))
	quickSort(arr, 0, len(arr) -1)
	print("result:\n")
	for s in arr:
		print(s)
