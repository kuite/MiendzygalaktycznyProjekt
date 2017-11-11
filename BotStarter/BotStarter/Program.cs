using System;
using System.Collections;
using System.Collections.Generic;
using System.Configuration;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using BotStarter.Model;

namespace BotStarter
{
    class Program
    {
        static void Main(string[] args)
        {
            DateTime lastEcoRun = DateTime.Now;
            DateTime lastDefRun = DateTime.Now;
            var defToRun = true;
            var ecoToRun = true;

            while (true)
            {
                TimeSpan elapsedSinceEcoRun = DateTime.Now - lastEcoRun;
                TimeSpan elapsedSinceDefRun = DateTime.Now - lastDefRun;

                #region defRun

                //                if (defToRun)
                //                {
                //                    try
                //                    {
                //                        for (int i = 0; i < 1; i++)
                //                        {
                //                            var defOutput = RunCmd(ConfigurationManager.AppSettings["Bot"], i.ToString());
                //                            Console.WriteLine(defOutput);
                //                        }
                //
                //                    }
                //                    catch (Exception e)
                //                    {
                //                        Console.WriteLine(e);
                //                    }
                //                    lastDefRun = DateTime.Now;
                //                    defToRun = false;
                //                }

                #endregion


                if (ecoToRun)
                {
                    try
                    {
                        var startTime = DateTime.Now;
                        Console.WriteLine($"<--Started loop at: {startTime}");
                        for (int i = 0; i < 20; i++)
                        {
                            
                            var ecoOutput = RunCmd(ConfigurationManager.AppSettings["Bot"], i.ToString());
                            if (!string.IsNullOrEmpty(ecoOutput))
                            {
                                Console.WriteLine(ecoOutput);
                            }
                            
                        }
                        var endTime = DateTime.Now;
                        TimeSpan delta = endTime - startTime;
                        Console.WriteLine($"<--Ended loop at: {endTime}, time elapsed: {delta.Minutes} [m] {delta.Seconds} [s]");
                    }
                    catch (Exception e)
                    {
                        Console.WriteLine(e);
                    }
                    finally
                    {
                        Thread.Sleep(1000 * 60 * 30); //30 minutes
                    }
                    //lastEcoRun = DateTime.Now;
                    //ecoToRun = false;
                }

//                if (elapsedSinceEcoRun.Minutes > 20)
//                {
//                    ecoToRun = true;
//                }

                if (elapsedSinceDefRun.Minutes > 60)
                {
                    defToRun = true;
                }
            }
        }

        private static string RunCmd(string cmd, string args)
        {
            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = ConfigurationManager.AppSettings["PythonPath"];
            start.Arguments = string.Format("{0} {1}", cmd, args);
            start.UseShellExecute = false;
            start.RedirectStandardOutput = true;
            using (Process process = Process.Start(start))
            {
                try
                {
                    process.WaitForExit(100 * 60 * 13);

                    using (StreamReader reader = process.StandardOutput)
                    {
                        string result = reader.ReadToEnd();
                        return result;
                    }
                }
                catch (Exception e)
                {
                    return e.Message;
                }
            }
        }
    }
}
