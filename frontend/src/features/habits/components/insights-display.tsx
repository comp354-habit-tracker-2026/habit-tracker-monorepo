import { useState} from 'react';
import { mockActivities } from '@/app/routes/app/mock-activities';
 export function InsightsDisplay() {
    const [show, setShow] = useState(false);
    const [start, setStart] = useState('2025-01-01');
    const [end, setEnd] = useState('2026-04-22')


    const currMonth = new Date();
    const startOfMonth = new Date(currMonth.getFullYear(), currMonth.getMonth(), 1);
    const endOfMonth = new Date(currMonth.getFullYear(), currMonth.getMonth() + 1, 0, 23, 59, 59);

    const currMonthActivities = mockActivities.filter(activity => {
      const date = new Date(activity.startedAt);
      if (start && end) {
        const startDate = new Date(start);
        const endDate = new Date(end);
        endDate.setHours(23, 59, 59);
        return date >= startDate && date <= endDate;
      }
      return date >= startOfMonth && date <= endOfMonth;
    });

    if (currMonthActivities.length === 0) {
      return (
        <div
        style={{
          padding: '12px',
          border: '1px solid #ccc',
          borderRadius: '8px',
          backgroundColor: '#f9fafb',
        }}
        >
          <h2 style = {{marginTop: 0, marginBottom: '10px', fontSize: '16px'}}>Insights</h2>
          <div>
            <label>From: <input type="date" value={start} onChange={e => setStart(e.target.value)} 
            style={{padding: '4px 6px', borderRadius: '6px',border: '1px solid #ccc',}}/></label>
            {' '}
            <label>To: <input type="date" value={end} onChange={e => setEnd(e.target.value)}
            style={{padding: '4px 6px', borderRadius: '6px',border: '1px solid #ccc',}} /></label>
          </div>
          <p>No activity data available for this range.</p>
        </div>
      );
    }

    const activitiesperDay: Record<string, number>={};
    const caloriesperDay: Record<string, number> = {};
    const activityTypeCount: Record<string, number> = {};

    let mostIntenseActivity = currMonthActivities[0];
    let totalHeartRate = 0;
    let heartrateCount = 0;

    for (const activity of currMonthActivities) {
        const date = activity.startedAt.slice(0, 10);
        activitiesperDay[date] = (activitiesperDay[date] ||0) +1;
        caloriesperDay[date] = (caloriesperDay[date] ||0) + (activity.summary.calories || 0);

        const type = activity.activityType || 'Unknown';
        activityTypeCount[type] = (activityTypeCount[type] || 0) + 1;
        if (
            (activity.summary.calories || 0) > (mostIntenseActivity.summary.calories || 0)

        ){
         mostIntenseActivity = activity;
        }
        if (activity.summary.avgHeartRate !== undefined) {
            totalHeartRate += activity.summary.avgHeartRate;
            heartrateCount +=1
         }
    }

    let mostActiveDay = '';
    let mostActivities = 0;

    for (const day in activitiesperDay) {
        if (activitiesperDay[day]> mostActivities) {
            mostActivities = activitiesperDay[day];
            mostActiveDay = day;
        }
    }

    let leastActiveDay = '';
    let leastActivities = Infinity;

    for (const day in activitiesperDay) {
      if (activitiesperDay[day] < leastActivities) {
        leastActivities = activitiesperDay[day];
        leastActiveDay = day;
      }
    }

    let highestCalorieDay = '';
    let highestCalories = 0;

    for (const day in caloriesperDay) {
        if (caloriesperDay[day]> highestCalories) {
            highestCalories = caloriesperDay[day];
            highestCalorieDay = day;
        }
    }

    //activity type breakdown
    let mostFrequentActivityType = '';
    let maxCount = 0;
    const totalActivities = currMonthActivities.length;

    for (const type in activityTypeCount) {
      if (activityTypeCount[type] > maxCount) {
        maxCount = activityTypeCount[type];
        mostFrequentActivityType = type;
      }
    }

    const activityTypePercentages: Record<string, number> = {};
    for (const type in activityTypeCount) {
      activityTypePercentages[type] = Math.round(
        (activityTypeCount[type] / totalActivities) * 100
      );
    }


    let monthlyCalories = 0;
    let monthlySteps = 0;

    for (const activity of currMonthActivities) {
      monthlyCalories += activity.summary.calories || 0;
      monthlySteps += activity.summary.steps || 0;
    }

    // Monthly comparison logic
    const now = new Date();
    let thisMonthCalories = 0;
    let lastMonthCalories = 0;

    for (const activity of currMonthActivities) {
      const date = new Date(activity.startedAt);
      const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));

      if (diffDays <= 7) {
        thisMonthCalories += activity.summary.calories || 0;
      } else if (diffDays <= 14) {
        lastMonthCalories += activity.summary.calories || 0;
      }
    }

    let calorieChange = 0;

    if (lastMonthCalories > 0) {
      calorieChange = Math.round(
        ((thisMonthCalories - lastMonthCalories) / lastMonthCalories) * 100
      );
    }

    const averageHeartRate = heartrateCount > 0 ? Math.round(totalHeartRate / heartrateCount) : 0;


    if(!show) {
        return (
        <button onClick={() => setShow(true)}
        style={{
          padding: '10px 20px',
          borderRadius: '10px',
          border: '1px solid #ccc',
          backgroundColor: '#f3f4f6',
          cursor: 'pointer',
          fontWeight: 500,
        }}>
        View your Insights
        </button> );
        }
        return (
        <div
        style={{
          position: 'relative',
          padding: '16px',
          border: '1px solid #ddd',
          borderRadius: '12px',
          backgroundColor: '#f9fafb',
          width: '100%',
          marginTop: '12px',
        }}
        >
          <h2 style = {{margin: 0, fontSize: '28px', fontWeight: '600px', textAlign: 'center'}}>
            Insights
          </h2>
             <button onClick={() => setShow(false)}
              style={{
                position: 'absolute',
                right: '20px',
                padding: '10px 20px',
                borderRadius: '10px',
                border: '1px solid #ccc',
                backgroundColor: '#f3f4f6',
                cursor: 'pointer',
                fontWeight: 500,
              }}>
                Hide Insights
                 </button>
                 <div style={{ marginTop: '12px', marginBottom: '16px'}}>
                   <label style={{ marginRight: '12px', fontSize: '15px' }}>
                    From: <input type="date" value={start} onChange={e => setStart(e.target.value)} 
                    style={{ padding: '6px 8px', borderRadius: '6px', border: '1px solid #ccc'}}/></label>
                   {' '}
                   <label>To: <input type="date" value={end} onChange={e => setEnd(e.target.value)} 
                   style={{ padding: '6px 8px', borderRadius: '6px', border: '1px solid #ccc'}}/></label>
                 </div>
                 <div>
                    <p style={{padding: '10px 20px', borderRadius: '10px', border: '1px solid #ccc', backgroundColor: '#f3f4f6', cursor: 'pointer', fontWeight: 500}}><strong>Most active day:</strong> {mostActiveDay} ({mostActivities} activities)</p>
                    <p style={{padding: '10px 20px', borderRadius: '10px', border: '1px solid #ccc', backgroundColor: '#f3f4f6', cursor: 'pointer', fontWeight: 500}}><strong>Least active day:</strong> {leastActiveDay} ({leastActivities} activities)</p>
                    <p style={{padding: '10px 20px', borderRadius: '10px', border: '1px solid #ccc', backgroundColor: '#f3f4f6', cursor: 'pointer', fontWeight: 500}}><strong>Highest calories in one day:</strong> {highestCalorieDay} ({highestCalories} calories)</p>
                    <p style={{padding: '10px 20px', borderRadius: '10px', border: '1px solid #ccc', backgroundColor: '#f3f4f6', cursor: 'pointer', fontWeight: 500}}><strong>Most intense activity:</strong> {mostIntenseActivity.title} ({mostIntenseActivity.activityType}) -{' '}
                     {mostIntenseActivity.summary.calories || 0} calories</p>
                    <p style={{padding: '10px 20px', borderRadius: '10px', border: '1px solid #ccc', backgroundColor: '#f3f4f6', cursor: 'pointer', fontWeight: 500}}><strong>Average heart rate:</strong> {averageHeartRate} bpm</p>
                    <p style={{padding: '10px 20px', borderRadius: '10px', border: '1px solid #ccc', backgroundColor: '#f3f4f6', cursor: 'pointer', fontWeight: 500}}><strong>Total calories:</strong> {monthlyCalories} kcal</p>
                    <p style={{padding: '10px 20px', borderRadius: '10px', border: '1px solid #ccc', backgroundColor: '#f3f4f6', cursor: 'pointer', fontWeight: 500}}><strong>Total steps:</strong> {monthlySteps}</p>
                    <p style={{padding: '10px 20px', borderRadius: '10px', border: '1px solid #ccc', backgroundColor: '#f3f4f6', cursor: 'pointer', fontWeight: 500}}>
                      <strong>Monthly trend:</strong>{' '}
                      {calorieChange >= 0
                        ? `+${calorieChange}% more calories than last month 📈`
                        : `${calorieChange}% fewer calories than last month 📉`}
                    </p>
                    <p style={{padding: '10px 20px', borderRadius: '10px', border: '1px solid #ccc', backgroundColor: '#f3f4f6', cursor: 'pointer', fontWeight: 500}}><strong>Most frequent activity:</strong> {mostFrequentActivityType} ({maxCount} times)</p>
                    <div style={{padding: '10px 20px', borderRadius: '10px', border: '1px solid #ccc', backgroundColor: '#f3f4f6', cursor: 'pointer', fontWeight: 500}}>
                    <p><strong>Activity breakdown:</strong></p>
                      <ul>
                      {Object.entries(activityTypePercentages).map(([type, percent]) => (
                        <li key={type}>
                          {type}: {percent}%
                        </li>
                        ))}
                      </ul>
                      </div>
                    </div>
                 </div>
                )
        }



