using System;

class Program
{
    static void Main(string[] args)
    {
        int n;
        string input;

        while (true)
        {
            Console.Write("Enter a number: ");
            input = Console.ReadLine();

            if (int.TryParse(input, out n))
            {
                break;
            }

            Console.WriteLine("Invalid input. Please enter a valid integer.");
        }

        if (n % 2 == 0)
        {
            Console.WriteLine("Even Number");
        }
        else
        {
            Console.WriteLine("Odd Number");
        }
    }
}
