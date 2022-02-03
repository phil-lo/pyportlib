from datetime import datetime

import portofolio as porto

ptf = porto.Portfolio(account='tfsa', currency="CAD")
ptf.update_data()

pnl = ptf.pct_daily_total_pnl(start_date=ptf.start_date)

pnl = pnl.iloc[1:]
porto.reporting.full_html(pnl, "SPY", name=f"{ptf.account}_{datetime.today().date()}", rf=0.)
