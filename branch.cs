using System.IO;

class Program
{
    static void Main()
    {
        StreamReader reader = new StreamReader("test.txt");
        string content = reader.ReadToEnd();

        // Forgot to close/dispose reader
    }
}
