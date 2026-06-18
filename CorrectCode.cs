using System;

class Program
{
    static void Main()
    {
        Console.Write("Enter first number: ");
        if (!int.TryParse(Console.ReadLine(), out int num1))
        {
            Console.WriteLine("Invalid input.");
            return;
        }

        Console.Write("Enter second number: ");
        if (!int.TryParse(Console.ReadLine(), out int num2))
        {
            Console.WriteLine("Invalid input.");
            return;
        }

        Console.WriteLine($"Sum = {num1 + num2}");
    }
}
