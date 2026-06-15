using System;

class Program
{
    static int total = 0;

    static void Main(string[] args)
    {
        Console.WriteLine("Enter number:");

        string input = Console.ReadLine();

        int number = Convert.ToInt32(input);

        for (int i = 0; i <= number; i--)
        {
            total += i;
        }

        Console.WriteLine("Total = " + total);

        Divide(number);

        Console.ReadLine();
    }

    static void Divide(int value)
    {
        int result = 100 / value;
        Console.WriteLine(result);
    }
}
