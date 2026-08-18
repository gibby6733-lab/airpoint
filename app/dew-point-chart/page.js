import Link from "next/link";

export const metadata = {
  title: "Dew Point Chart | AirPoint",
  description:
    "Use this dew point chart to understand humidity levels and how different dew points generally feel.",
};

const rows = [
  ["Below 50°F", "Below 10°C", "Comfortably dry"],
  ["50–59°F", "10–15°C", "Comfortable"],
  ["60–64°F", "16–18°C", "Slightly humid"],
  ["65–69°F", "18–21°C", "Humid"],
  ["70–74°F", "21–23°C", "Very humid"],
  ["75°F+", "24°C+", "Extremely humid"],
];

export default function DewPointChart() {
  return (
    <main className="site">
      <section className="hero">
        <div className="container">
          <div className="badge">AIRPOINT GUIDE</div>

          <h1>Dew Point Chart</h1>

          <p className="heroText">
            A quick reference for understanding dew point and how different
            moisture levels generally feel.
          </p>

          <Link href="/" className="backLink">
            ← Calculate Dew Point
          </Link>
        </div>
      </section>

      <section className="content">
        <div className="container narrow">
          <h2>Dew point reference</h2>

          <p>
            Dew point is a measure of atmospheric moisture. Generally, the
            higher the dew point, the more moisture is present in the air.
          </p>

          <div className="tableWrap">
            <table>
              <thead>
                <tr>
                  <th>Dew Point °F</th>
                  <th>Dew Point °C</th>
                  <th>General Description</th>
                </tr>
              </thead>

              <tbody>
                {rows.map((row) => (
                  <tr key={row[0]}>
                    <td>{row[0]}</td>
                    <td>{row[1]}</td>
                    <td>{row[2]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <h2>What does a high dew point mean?</h2>

          <p>
            A high dew point means the air contains a relatively large amount
            of water vapor. High dew points often make outdoor conditions feel
            more humid or muggy.
          </p>

          <h2>What does a low dew point mean?</h2>

          <p>
            A lower dew point generally means there is less moisture in the
            air. Low dew points often correspond with drier-feeling
            conditions.
          </p>

          <h2>Calculate your dew point</h2>

          <p>
            A chart provides a quick reference, but you can calculate a more
            specific dew point using your exact temperature and relative
            humidity.
          </p>

          <Link href="/" className="primaryLink">
            Open Dew Point Calculator →
          </Link>

          <h2>Related guides</h2>

          <ul className="linkList">
            <li>
              <Link href="/what-is-dew-point">What Is Dew Point?</Link>
            </li>
            <li>
              <Link href="/dew-point-vs-humidity">
                Dew Point vs. Humidity
              </Link>
            </li>
          </ul>
        </div>
      </section>
    </main>
  );
}