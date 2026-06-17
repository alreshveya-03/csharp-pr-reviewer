using System;

public class Calculator
{
    /// <summary>
    /// Adds two integers.
    /// </summary>
    public static int Add(int firstNumber, int secondNumber)
    {
        checked
        {
            return firstNumber + secondNumber;
        }
    }

    /// <summary>
    /// Subtracts the second integer from the first.
    /// </summary>
    public static int Subtract(int firstNumber, int secondNumber)
    {
        checked
        {
            return firstNumber - secondNumber;
        }
    }
}

public class Program
{
    public static void Main()
    {
        try
        {
            int sum = Calculator.Add(10, 20);
            int difference = Calculator.Subtract(20, 10);

            Console.WriteLine($"Sum: {sum}");
            Console.WriteLine($"Difference: {difference}");
        }
        catch (OverflowException)
        {
            Console.WriteLine("Arithmetic overflow occurred.");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"An unexpected error occurred: {ex.Message}");
        }
    }
}