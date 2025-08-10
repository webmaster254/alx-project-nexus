import React, { useState, useEffect } from 'react';
import { 
  Briefcase, 
  Building, 
  FileText, 
  Plus, 
  Search, 
  Filter,
  Edit,
  Trash2,
  Eye,
  XCircle,
  AlertCircle,
  TrendingUp
} from 'lucide-react';
import { adminService, applicationService, companyService, categoryService } from '../services';
import type { AdminJob, AdminCompany } from '../services/adminService';
import type { Application } from '../services/applicationService';
import type { Industry, JobType } from '../services/categoryService';
import JobForm from '../components/admin/JobForm';

const AdminDashboardPage: React.FC = () => {
  // State management
  const [activeTab, setActiveTab] = useState<'overview' | 'jobs' | 'companies' | 'applications' | 'categories'>('overview');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [applicationsLoading, setApplicationsLoading] = useState(false);

  // Dashboard stats
  const [dashboardStats, setDashboardStats] = useState({
    total_jobs: 0,
    active_jobs: 0,
    featured_jobs: 0,
    total_companies: 0,
    verified_companies: 0,
    total_applications: 0,
    pending_applications: 0,
    total_users: 0,
    active_users: 0,
    jobs_this_month: 0,
    applications_this_month: 0
  });

  // Data states
  const [jobs, setJobs] = useState<AdminJob[]>([]);
  const [companies, setCompanies] = useState<AdminCompany[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [jobTypes, setJobTypes] = useState<JobType[]>([]);
  
  // Pagination and filters
  const [currentPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedItems, setSelectedItems] = useState<number[]>([]);

  // Modal states
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingItem, setEditingItem] = useState<any>(null);

  // Load dashboard data
  useEffect(() => {
    loadDashboardStats();
  }, []);

  // Load data based on active tab
  useEffect(() => {
    loadTabData();
  }, [activeTab, currentPage, searchQuery]);

  const loadDashboardStats = async () => {
    try {
      const stats = await adminService.getDashboardStats();
      setDashboardStats(stats);
    } catch (error) {
      console.error('Failed to load dashboard stats:', error);
    }
  };

  const loadTabData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      switch (activeTab) {
        case 'jobs':
          const jobsData = await adminService.getAllJobs({
            search: searchQuery,
            page: currentPage,
            page_size: 20
          });
          setJobs(jobsData.results);
          break;
          
        case 'companies':
          const companiesData = await companyService.getCompanies({
            search: searchQuery,
            page: currentPage,
            page_size: 20
          });
          setCompanies(companiesData.results.map(company => ({
            ...company,
            jobs_count: company.jobs_count || 0
          })));
          break;
          
        case 'applications':
          setApplicationsLoading(true);
          try {
            // Try to get pending applications first (faster endpoint)
            const applicationsData = await applicationService.getPendingApplications({
              search: searchQuery,
              page: currentPage,
              page_size: 20
            });
            setApplications(applicationsData.results);
            console.log(`Loaded ${applicationsData.results.length} pending applications`);
          } catch (pendingError) {
            console.warn('Failed to load pending applications, trying all applications:', pendingError);
            try {
              // Fallback to all applications with shorter timeout
              const applicationsData = await applicationService.getApplications({
                search: searchQuery,
                page: currentPage,
                page_size: 5 // Even smaller page size for faster loading
              });
              setApplications(applicationsData.results);
              console.log(`Loaded ${applicationsData.results.length} applications`);
            } catch (allError: any) {
              console.error('Failed to load applications:', allError);
              // Show a meaningful error message for timeout issues
              if (allError?.code === 'TIMEOUT' || allError?.status === 408) {
                setError('Applications are taking too long to load. This usually happens when there are many applications in the system. Try refreshing or contact your system administrator.');
              } else {
                setError('Unable to load applications. The applications endpoint may be experiencing issues.');
              }
              // Set empty applications array to prevent UI issues
              setApplications([]);
            }
          } finally {
            setApplicationsLoading(false);
          }
          break;
          
        case 'categories':
          const [industriesData, jobTypesData] = await Promise.all([
            categoryService.getIndustries({ search: searchQuery }),
            categoryService.getJobTypes({ search: searchQuery })
          ]);
          setIndustries(industriesData.results);
          setJobTypes(jobTypesData.results);
          break;
      }
    } catch (error) {
      setError('Failed to load data');
      console.error('Failed to load tab data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (type: string, id: number) => {
    if (!confirm('Are you sure you want to delete this item?')) return;
    
    try {
      switch (type) {
        case 'job':
          await adminService.deleteJob(id);
          break;
        case 'company':
          await companyService.deleteCompany(id);
          break;
        case 'application':
          await applicationService.deleteApplication(id);
          break;
        case 'industry':
          await categoryService.deleteIndustry(id);
          break;
        case 'jobType':
          await categoryService.deleteJobType(id);
          break;
      }
      loadTabData();
      loadDashboardStats();
    } catch (error) {
      alert('Failed to delete item');
      console.error('Delete error:', error);
    }
  };

  const handleBulkAction = async (action: string) => {
    if (selectedItems.length === 0) {
      alert('Please select items first');
      return;
    }

    try {
      switch (action) {
        case 'delete':
          if (!confirm(`Delete ${selectedItems.length} selected items?`)) return;
          
          if (activeTab === 'jobs') {
            await adminService.bulkDeleteJobs(selectedItems);
          } else if (activeTab === 'companies') {
            await companyService.bulkDeleteCompanies(selectedItems);
          }
          break;
          
        case 'activate':
          if (activeTab === 'jobs') {
            await adminService.bulkUpdateJobs(selectedItems, { is_active: true });
          } else if (activeTab === 'companies') {
            await companyService.bulkUpdateCompanies(selectedItems, { is_active: true });
          }
          break;
          
        case 'deactivate':
          if (activeTab === 'jobs') {
            await adminService.bulkUpdateJobs(selectedItems, { is_active: false });
          } else if (activeTab === 'companies') {
            await companyService.bulkUpdateCompanies(selectedItems, { is_active: false });
          }
          break;
      }
      
      setSelectedItems([]);
      loadTabData();
      loadDashboardStats();
    } catch (error) {
      alert('Bulk action failed');
      console.error('Bulk action error:', error);
    }
  };

  // Overview Dashboard
  const OverviewTab = () => (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Jobs</p>
              <p className="text-2xl font-semibold text-gray-900">{dashboardStats.total_jobs}</p>
              <p className="text-xs text-gray-400">{dashboardStats.active_jobs} active</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <Briefcase className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Companies</p>
              <p className="text-2xl font-semibold text-gray-900">{dashboardStats.total_companies}</p>
              <p className="text-xs text-gray-400">{dashboardStats.verified_companies} verified</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <Building className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Applications</p>
              <p className="text-2xl font-semibold text-gray-900">{dashboardStats.total_applications}</p>
              <p className="text-xs text-gray-400">{dashboardStats.pending_applications} pending</p>
            </div>
            <div className="p-3 bg-yellow-100 rounded-lg">
              <FileText className="h-6 w-6 text-yellow-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Featured Jobs</p>
              <p className="text-2xl font-semibold text-gray-900">{dashboardStats.featured_jobs}</p>
              <p className="text-xs text-gray-400">promoted listings</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <TrendingUp className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button
            onClick={() => { setActiveTab('jobs'); setShowCreateModal(true); }}
            className="flex items-center justify-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Plus className="h-5 w-5 text-blue-600 mr-2" />
            <span className="text-sm text-gray-700">Create Job</span>
          </button>
          
          <button
            onClick={() => { setActiveTab('companies'); setShowCreateModal(true); }}
            className="flex items-center justify-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Plus className="h-5 w-5 text-green-600 mr-2" />
            <span className="text-sm text-gray-700">Add Company</span>
          </button>
          
          <button
            onClick={() => setActiveTab('applications')}
            className="flex items-center justify-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Eye className="h-5 w-5 text-yellow-600 mr-2" />
            <span className="text-sm text-gray-700">Review Apps</span>
          </button>
          
          <button
            onClick={() => setActiveTab('categories')}
            className="flex items-center justify-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Filter className="h-5 w-5 text-purple-600 mr-2" />
            <span className="text-sm text-gray-700">Manage Categories</span>
          </button>
        </div>
      </div>
    </div>
  );

  // Data Table Component
  const DataTable = ({ data, type }: { data: any[]; type: string }) => (
    <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900 capitalize">{type} Management</h3>
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="h-4 w-4 mr-2" />
            Create {type.slice(0, -1)}
          </button>
        </div>
        
        {/* Search and Filters */}
        <div className="mt-4 flex items-center space-x-4">
          <div className="flex-1 relative">
            <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder={`Search ${type}...`}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          {selectedItems.length > 0 && (
            <div className="flex space-x-2">
              <button
                onClick={() => handleBulkAction('activate')}
                className="px-3 py-2 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700"
              >
                Activate ({selectedItems.length})
              </button>
              <button
                onClick={() => handleBulkAction('deactivate')}
                className="px-3 py-2 bg-yellow-600 text-white rounded-lg text-sm hover:bg-yellow-700"
              >
                Deactivate ({selectedItems.length})
              </button>
              <button
                onClick={() => handleBulkAction('delete')}
                className="px-3 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700"
              >
                Delete ({selectedItems.length})
              </button>
            </div>
          )}
        </div>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="w-12 px-6 py-3 text-left">
                <input
                  type="checkbox"
                  checked={selectedItems.length === data.length && data.length > 0}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedItems(data.map(item => item.id));
                    } else {
                      setSelectedItems([]);
                    }
                  }}
                  className="rounded border-gray-300"
                />
              </th>
              {type === 'jobs' && (
                <>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Company</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Applications</th>
                </>
              )}
              {type === 'companies' && (
                <>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Industry</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Size</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Jobs</th>
                </>
              )}
              {type === 'applications' && (
                <>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Applicant</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Job</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Company</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Applied</th>
                </>
              )}
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {data.map((item) => (
              <tr key={item.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <input
                    type="checkbox"
                    checked={selectedItems.includes(item.id)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedItems([...selectedItems, item.id]);
                      } else {
                        setSelectedItems(selectedItems.filter(id => id !== item.id));
                      }
                    }}
                    className="rounded border-gray-300"
                  />
                </td>
                
                {type === 'jobs' && (
                  <>
                    <td className="px-6 py-4">
                      <div className="font-medium text-gray-900">{item.title}</div>
                      <div className="text-sm text-gray-500">{item.job_type?.name}</div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">{item.company?.name}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{item.location}</td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        item.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {item.is_active ? 'Active' : 'Inactive'}
                      </span>
                      {item.is_featured && (
                        <span className="ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-purple-100 text-purple-800">
                          Featured
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">{item.applications_count || 0}</td>
                  </>
                )}
                
                {type === 'companies' && (
                  <>
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        {item.logo && (
                          <img src={item.logo} alt="" className="h-8 w-8 rounded-full mr-3" />
                        )}
                        <div>
                          <div className="font-medium text-gray-900">{item.name}</div>
                          {item.website && (
                            <div className="text-sm text-gray-500">{item.website}</div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">{item.industry?.name || 'N/A'}</td>
                    <td className="px-6 py-4 text-sm text-gray-900 capitalize">{item.size || 'N/A'}</td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        item.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {item.is_active ? 'Active' : 'Inactive'}
                      </span>
                      {item.is_verified && (
                        <span className="ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                          Verified
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">{item.jobs_count || 0}</td>
                  </>
                )}
                
                {type === 'applications' && (
                  <>
                    <td className="px-6 py-4">
                      <div className="font-medium text-gray-900">
                        {item.user?.first_name} {item.user?.last_name}
                      </div>
                      <div className="text-sm text-gray-500">{item.user?.email}</div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">{item.job?.title}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{item.job?.company?.name}</td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        item.status?.name === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                        item.status?.name === 'accepted' ? 'bg-green-100 text-green-800' :
                        item.status?.name === 'rejected' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {item.status?.name || 'Unknown'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {new Date(item.applied_at).toLocaleDateString()}
                    </td>
                  </>
                )}
                
                <td className="px-6 py-4 text-right">
                  <div className="flex items-center justify-end space-x-2">
                    <button
                      onClick={() => {
                        setEditingItem(item);
                        setShowEditModal(true);
                      }}
                      className="p-1 text-gray-400 hover:text-blue-600"
                    >
                      <Edit className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(type.slice(0, -1), item.id)}
                      className="p-1 text-gray-400 hover:text-red-600"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
          <p className="text-gray-600 mt-2">Manage your job board platform</p>
        </div>

        {/* Navigation Tabs */}
        <div className="mb-8">
          <nav className="flex space-x-8 border-b border-gray-200">
            {[
              { key: 'overview', label: 'Overview', icon: TrendingUp },
              { key: 'jobs', label: 'Jobs', icon: Briefcase },
              { key: 'companies', label: 'Companies', icon: Building },
              { key: 'applications', label: 'Applications', icon: FileText },
              { key: 'categories', label: 'Categories', icon: Filter }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key as any)}
                  className={`flex items-center px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === tab.key
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-4 w-4 mr-2" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Content */}
        <div>
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center">
                <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
                <span className="text-red-800">{error}</span>
              </div>
            </div>
          )}

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <>
              {activeTab === 'overview' && <OverviewTab />}
              {activeTab === 'jobs' && <DataTable data={jobs} type="jobs" />}
              {activeTab === 'companies' && <DataTable data={companies} type="companies" />}
              {activeTab === 'applications' && (
                applicationsLoading ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="text-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                      <p className="text-gray-600">Loading applications...</p>
                      <p className="text-sm text-gray-500 mt-2">This may take a moment for large datasets</p>
                    </div>
                  </div>
                ) : (
                  <DataTable data={applications} type="applications" />
                )
              )}
              {activeTab === 'categories' && (
                <div className="space-y-8">
                  <div className="bg-white p-6 rounded-lg shadow-sm border">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Industries</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {industries.map((industry) => (
                        <div key={industry.id} className="p-4 border border-gray-200 rounded-lg">
                          <div className="flex items-center justify-between">
                            <div>
                              <h4 className="font-medium text-gray-900">{industry.name}</h4>
                              {industry.description && (
                                <p className="text-sm text-gray-500 mt-1">{industry.description}</p>
                              )}
                            </div>
                            <div className="flex space-x-1">
                              <button
                                onClick={() => {
                                  setEditingItem(industry);
                                  setShowEditModal(true);
                                }}
                                className="p-1 text-gray-400 hover:text-blue-600"
                              >
                                <Edit className="h-4 w-4" />
                              </button>
                              <button
                                onClick={() => handleDelete('industry', industry.id)}
                                className="p-1 text-gray-400 hover:text-red-600"
                              >
                                <Trash2 className="h-4 w-4" />
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="bg-white p-6 rounded-lg shadow-sm border">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Job Types</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {jobTypes.map((jobType) => (
                        <div key={jobType.id} className="p-4 border border-gray-200 rounded-lg">
                          <div className="flex items-center justify-between">
                            <div>
                              <h4 className="font-medium text-gray-900">{jobType.name}</h4>
                              {jobType.description && (
                                <p className="text-sm text-gray-500 mt-1">{jobType.description}</p>
                              )}
                            </div>
                            <div className="flex space-x-1">
                              <button
                                onClick={() => {
                                  setEditingItem(jobType);
                                  setShowEditModal(true);
                                }}
                                className="p-1 text-gray-400 hover:text-blue-600"
                              >
                                <Edit className="h-4 w-4" />
                              </button>
                              <button
                                onClick={() => handleDelete('jobType', jobType.id)}
                                className="p-1 text-gray-400 hover:text-red-600"
                              >
                                <Trash2 className="h-4 w-4" />
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Job Creation/Edit Modal */}
        {(showCreateModal || showEditModal) && activeTab === 'jobs' && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  {showCreateModal ? 'Create New Job' : 'Edit Job'}
                </h3>
                <button
                  onClick={() => {
                    setShowCreateModal(false);
                    setShowEditModal(false);
                    setEditingItem(null);
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="h-6 w-6" />
                </button>
              </div>
              
              <JobForm
                job={editingItem}
                onSubmit={async (jobData) => {
                  try {
                    if (showCreateModal) {
                      await adminService.createJob(jobData);
                    } else if (editingItem) {
                      await adminService.updateJob(editingItem.id, jobData);
                    }
                    
                    // Close modal and refresh data
                    setShowCreateModal(false);
                    setShowEditModal(false);
                    setEditingItem(null);
                    loadTabData();
                    loadDashboardStats();
                  } catch (error) {
                    console.error('Failed to save job:', error);
                    alert('Failed to save job. Please try again.');
                  }
                }}
                onCancel={() => {
                  setShowCreateModal(false);
                  setShowEditModal(false);
                  setEditingItem(null);
                }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboardPage;