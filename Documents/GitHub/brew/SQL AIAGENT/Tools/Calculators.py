from typing import List, Callable
import json

class Calculator():
    def __init__(self, **kwargs):
        tools:List[Callable]=[
            self.add,
            self.subtract,
            self.multiply,
            self.divide,
            self.exponentiate,
            self.factorial,
            self.is_prime,
            self.square_root,
        ]
        #initialize the toolkit with auto-registration enabled
        #super().__init__(name="calculator", tools=tools, **kwargs)
    
    def add(self, a:float, b:float)-> str:
        """add Two number and return the result.

        Args:
            a (float): first number.
            b (float): second number.

        Returns:
            str: JSON string of the result   
        """
        result = a+b
        
        return json.dumps({"operation": "addition", "result":result})

    def subtract(self, a:float, b:float)->str:
        """subtract two number and return the result.
        
        Args:
            a (float): first number.
            b (float): second number.
            
        Returns:
            str: JSON string of the result
        """
        result = a-b
        return json.dumps({"operation":"subtraction","result":result})

    def multiply(self, a:float, b:float)->str:
        """
        multiply two number and return the result.

        Args:
            a (float): first number.
            b (float): second number.
        
        Returns:
            str: JSON string of the result
        """
        result = a*b
        return json.dumps({"operation":"multiply","result":result})

    def divide(self, a:float,b:float)->str:
        """
        Divide two number and return the result.
        
        Args:
            a (float): dividend or Numerator.
            b (float): divisor or Denominator.
        
        Returns:
            str: JSON string of the result
        """
        if b==0:
            raise SyntaxError(json.dump({"operation":"division", "error":"Division by zero is undefined."}))
        result = a/b
        return json.dumps({"operation":"division","result":result})
    
    def exponentiate(self, a:float,b:float)->str:
        """Raise first number to the power of the second number an return the result
        
        Args:
            a (float): Base.
            b (float): Exponent.
            
        Returns:
            str: JSON string of the result
        """
        result = a**b
        return json.dumps({"operation":"exponentiation","result":result})
    
    def factorial(self, a:int)->str:
        """Calculate the factorial of a number and return the result

        Args:
            a (int): Number to calculate the factorial of.

        Returns:
            str: JSON string of the result.
        """
        if a<0:
            raise ValueError(json.dumps({"operation":"factorial","Error":"The input must be greater than 0!!"}))
        def compute(n:int)->int:
            if n == 0 or n ==1:
                return 1
            else:
                return n * compute(n - 1)
        result = compute(a)
        return json.dumps({"operation":"factorial","result":result})
    
    def is_prime(self, a:int)->str:
        """To verify the number is prime number or even number, return the result
        
        Args:
            a (int): number to be verify if prime.
        
        Returns:
            str: JSON string of the result.
        """
        if a<=1:
            return json.dumps({"operation": "prime_check", "result":False})
        for i in range(2, int(n**2 +1)):
            if a%i==0:
                return json.dumps({"operation": "prime_check", "result":False})
        return json.dumps({"operation": "prime_check", "result":True})
    
    def square_root(self,a:float)->str:
        """Calculate the square root of a number and return the result
        
        Args:
            a (float): Number to calculate the square root of.
        
        Returns:
            str: JSON string of the result.
        """
        if a<0:
            raise ValueError("The input need to be greater than 0!!")
        result= a **0.5
        return json.dumps({"operation": "square_root", "result":result})
print(Calculator())