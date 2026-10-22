import { useState } from 'react';
import { Sidebar, type TabType } from './components/Sidebar';
import { Header } from './components/Header';
import { DashboardView } from './views/DashboardView';
import { StudentsView } from './views/StudentsView';
import { PaymentsView } from './views/PaymentsView';
import { DebtorsView } from './views/DebtorsView';
import type { Student, Debtor } from './types';

export function App() {
  const [currentTab, setCurrentTab] = useState<TabType>('dashboard');
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState<boolean>(false);
  const [refreshTrigger, setRefreshTrigger] = useState<number>(0);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  // Quick Action States
  const [isAddStudentOpen, setIsAddStudentOpen] = useState<boolean>(false);
  const [isRecordPaymentOpen, setIsRecordPaymentOpen] = useState<boolean>(false);
  const [preselectedStudent, setPreselectedStudent] = useState<Student | null>(null);

  const triggerRefresh = () => {
    setIsRefreshing(true);
    setRefreshTrigger((prev) => prev + 1);
    setTimeout(() => {
      setIsRefreshing(false);
    }, 600);
  };

  const handleRecordPaymentForStudent = (student: Student) => {
    setPreselectedStudent(student);
    setCurrentTab('payments');
  };

  const handleRecordPaymentForDebtor = (debtor: Debtor) => {
    const studentAsObj: Student = {
      id: debtor.student_id,
      name: debtor.name,
      phone: debtor.phone,
      group_name: debtor.group_name,
      monthly_fee: debtor.debt > 0 ? debtor.debt : debtor.monthly_fee,
      created_at: '',
      updated_at: '',
    };
    setPreselectedStudent(studentAsObj);
    setCurrentTab('payments');
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex">
      {/* Sidebar for Navigation */}
      <Sidebar
        currentTab={currentTab}
        onTabChange={(tab) => {
          setCurrentTab(tab);
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }}
        isOpen={isMobileSidebarOpen}
        onClose={() => setIsMobileSidebarOpen(false)}
      />

      {/* Main Content Area */}
      <div className="flex-1 lg:pl-72 flex flex-col min-h-screen min-w-0">
        {/* Sticky Header */}
        <Header
          currentTab={currentTab}
          onOpenMobileMenu={() => setIsMobileSidebarOpen(true)}
          onRefresh={triggerRefresh}
          isRefreshing={isRefreshing}
          onAddStudent={() => {
            if (currentTab !== 'students') {
              setCurrentTab('students');
            }
            setIsAddStudentOpen(true);
          }}
          onRecordPayment={() => {
            if (currentTab !== 'payments') {
              setCurrentTab('payments');
            }
            setIsRecordPaymentOpen(true);
          }}
        />

        {/* Page Content Body */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          {currentTab === 'dashboard' && (
            <DashboardView
              onNavigateToStudents={() => setCurrentTab('students')}
              onNavigateToPayments={() => setCurrentTab('payments')}
              onNavigateToDebtors={() => setCurrentTab('debtors')}
              onOpenPaymentModal={() => {
                setCurrentTab('payments');
                setIsRecordPaymentOpen(true);
              }}
              onOpenAddStudentModal={() => {
                setCurrentTab('students');
                setIsAddStudentOpen(true);
              }}
              refreshTrigger={refreshTrigger}
            />
          )}

          {currentTab === 'students' && (
            <StudentsView
              onRecordPaymentForStudent={handleRecordPaymentForStudent}
              refreshTrigger={refreshTrigger}
              onDataChanged={triggerRefresh}
              isAddModalOpenFromHeader={isAddStudentOpen}
              onCloseAddModalFromHeader={() => setIsAddStudentOpen(false)}
            />
          )}

          {currentTab === 'payments' && (
            <PaymentsView
              refreshTrigger={refreshTrigger}
              onDataChanged={triggerRefresh}
              preselectedStudent={preselectedStudent}
              onClearPreselectedStudent={() => setPreselectedStudent(null)}
              isCreateModalOpenFromHeader={isRecordPaymentOpen}
              onCloseCreateModalFromHeader={() => setIsRecordPaymentOpen(false)}
            />
          )}

          {currentTab === 'debtors' && (
            <DebtorsView
              onRecordPaymentForDebtor={handleRecordPaymentForDebtor}
              refreshTrigger={refreshTrigger}
            />
          )}
        </main>

        {/* Global Footer */}
        <footer className="border-t border-slate-200 bg-white py-4 px-6 text-center text-xs text-slate-500">
          <p>© 2026 Ecomdev Learning Center Payment Tracker • Barcha huquqlar himoyalangan</p>
        </footer>
      </div>
    </div>
  );
}

export default App;
