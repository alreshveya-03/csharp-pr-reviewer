// Suggested Fix:
using System;

public static class NumberChecker
{
    public static bool IsEven(int number)
    {
        return number % 2 == 0;
    }
}

class Program
{
    static void Main(string[] args)
    {
        Console.Write("Enter a number: ");
        string input = Console.ReadLine();

        if (int.TryParse(input, out int n))
        {
            if (NumberChecker.IsEven(n))
            {
                Console.WriteLine("Even Number");
            }
            else
            {
                Console.WriteLine("Odd Number");
            }
        }
        else
        {
            Console.WriteLine("Invalid input. Please enter a valid number.");
        }
    }
}
